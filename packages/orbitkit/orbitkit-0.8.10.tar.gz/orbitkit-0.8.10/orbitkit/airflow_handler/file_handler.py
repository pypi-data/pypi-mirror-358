import datetime
import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Tuple, Any, Optional
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, MetaData, Table, select, Column, Integer, insert, and_, asc, desc, text, delete, update

logger = logging.getLogger(__name__)


class FileFlowHandle:

    def __init__(self, not_allow_file_type_list=None, postgre_url=None):
        self.postgre_url = postgre_url or os.environ['PG_URI_AIRFLOW12_USER_NEWSFEEDSITE']
        if not self.postgre_url:
            raise ValueError("mongo_url cannot be None or empty. Please provide a valid mongo_url.")
        self.databases = "process_net"
        self.postgres_engine = create_engine(f"{self.postgre_url}/{self.databases}")
        self.postgres_session = sessionmaker(bind=self.postgres_engine)
        self.Session = scoped_session(self.postgres_session)
        self.postgres_metadata = MetaData()

        self.table_op_attachment = Table(
            'op_attachment', self.postgres_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            autoload_with=self.postgres_engine, schema='public'
        )
        self.table_op_meta = Table(
            'op_meta', self.postgres_metadata,
            autoload_with=self.postgres_engine, schema='public'
        )
        self.table_op_step = Table(
            'op_step', self.postgres_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            autoload_with=self.postgres_engine, schema='public'
        )

        self.table_op_meta_backup = Table(
            'op_meta_backup', self.postgres_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            autoload_with=self.postgres_engine, schema='public'
        )

        self.not_allow_file_type_list = not_allow_file_type_list or ['.xhtml']

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            self.Session.remove()

    def _validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        required_fields = ['start_stage', 'target_stage', 'tag_name']
        for field in required_fields:
            if not params.get(field):
                if field in ['start_stage', 'target_stage'] and params.get(field) not in ['convert', 'extract',
                                                                                          'embedding']:
                    return False, f"The value of '{field}' must be one of ['convert', 'extract', 'embedding']."
                return False, f"'{field}' cannot be empty."

        if int(params.get('priority')) > 10:
            return False, f"The priority of '{params.get('priority')}' must be greater than 10."

        allowed_methods = {"netmind", "pdfplumber"}
        if params.get("extract_method") not in allowed_methods:
            return False, f"Invalid extract_method: {params.get('extract_method')}. Allowed: {allowed_methods}"

        return True, ""

    def _validate_record(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        if not record.get('id'):
            return False, "Record 'id' is required."
        if not record.get('s3_path_info'):
            return False, "'s3_path_info' is required and cannot be empty."
        for i in record['s3_path_info']:
            if not i.get('store_path') or not i.get('file_name'):
                return False, "'store_path' or 'file_name' is required and cannot be empty."
            file_type = '.' + str(i['store_path']).split('.')[-1].lower()
            if self.not_allow_file_type_list and file_type in self.not_allow_file_type_list:
                return False, f"'file_type' {file_type} is invalid."
        return True, ""

    def _get_existing_ids(self, ids: List[str]) -> List[str]:
        if not ids:
            return []

        stmt = select(self.table_op_meta.c.id).where(self.table_op_meta.c.id.in_(ids))
        with self.session_scope() as session:
            result = session.execute(stmt)
            return [row[0] for row in result.fetchall()]

    def _check_records(self, records: List[Dict[str, Any]]) -> Tuple[bool, List[str], str]:
        ids = []
        record_count = 0
        for record in records:
            record_count += 1
            is_valid, msg = self._validate_record(record)
            if not is_valid:
                return False, [record.get("id", "unknown")], msg
            ids.append(record["id"])

        existing_ids = self._get_existing_ids(ids)
        if len(existing_ids) == record_count:
            return False, existing_ids, "No new data has been inserted."
        return True, existing_ids, f"Validation complete. total: {len(records)}. {len(existing_ids)} records already exist."

    def _build_insert_data(
            self, record: Dict[str, Any], params: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
        now = datetime.datetime.now(datetime.timezone.utc)
        attachments = []
        for item in record['s3_path_info']:
            file_type = '.' + str(item['store_path']).split('.')[-1].lower()
            attachments.append({
                'meta_id': record['id'],
                'store_path': item['store_path'],
                'file_name': item['file_name'],
                'file_type': file_type,
                'category': 'x_attachments' if params['start_stage'] == 'convert' else 'x_attachments_pdf',
                'created_at': now
            })
        tags = params.get('tags_extend') or []
        meta = {
            'id': record['id'],
            'propagation_id': record['id'],
            'priority': params['priority'],
            'status': 'init',
            'start_stage': params['start_stage'],
            'current_stage': params['current_stage'],
            'target_stage': params['target_stage'],
            'data_source': params['source_type'],
            'created_at': now,
            'updated_at': now,
            'tags': [params['tag_name'], params['extract_method']] + tags,
        }

        step = {
            'meta_id': record['id'],
            'stage': 'init',
            'status': 'init',
            'created_at': now
        }

        return attachments, meta, step

    def _insert_data_to_queue(self, insert_info: List[Dict[str, Any]]):
        with self.session_scope() as session:
            for item in insert_info:
                table = item['table']
                insert_data = item['data']
                stmt = insert(table)
                session.execute(stmt, insert_data)

    def _delete_and_backup_data_from_queue(self, postgres_coon, op_meta_id):
        op_meta_stmt = select(self.table_op_meta).where(text("id = :op_meta_id"))
        op_meta_data = postgres_coon.execute(op_meta_stmt, {'op_meta_id': op_meta_id}).mappings().one_or_none()

        if not op_meta_data:
            logger.warning(f"No data found in 'table' for op_meta ID: {op_meta_id}")
            return

        op_meta_data = dict(op_meta_data)

        op_x_attachments_stmt = select(self.table_op_attachment).where(text("meta_id = :op_meta_id"))
        op_x_attachments_data = postgres_coon.execute(op_x_attachments_stmt, {'op_meta_id': op_meta_id}).fetchall()

        created_at = op_meta_data['created_at'].isoformat()
        updated_at = op_meta_data['updated_at'].isoformat()

        x_attachments = []
        for attachment_row in op_x_attachments_data:
            attachment = dict(attachment_row._mapping)
            attachment.update({
                'created_at': created_at,
                'updated_at': updated_at
            })
            x_attachments.append(attachment)

        op_meta_data.update({
            'x_attachments': x_attachments,
            'report_id': op_meta_id,
            'created_at': created_at,
            'updated_at': updated_at
        })
        op_meta_data.pop('id', None)

        logger.info(f"备份数据 {op_meta_id} {op_meta_data}")
        stmt_insert_history = insert(self.table_op_meta_backup)
        postgres_coon.execute(stmt_insert_history, op_meta_data)

        logger.info(f"删除行 {op_meta_id}")
        stmt_del_op_meta = delete(self.table_op_meta).where(self.table_op_meta.c.id == op_meta_id)
        stmt_del_op_x_attachments = delete(self.table_op_attachment).where(
            self.table_op_attachment.c.meta_id == op_meta_id)
        compiled_sql = stmt_del_op_meta.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        print(str(compiled_sql))

        compiled_sql2 = stmt_del_op_x_attachments.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        print(str(compiled_sql2))
        postgres_coon.execute(stmt_del_op_meta)
        postgres_coon.execute(stmt_del_op_x_attachments)

    def _update_failed_record_to_manual(self, postgres_coon, op_meta_id):
        op_meta_stmt = (
            update(self.table_op_meta)
            .where(text("id = :op_meta_id"))
            .values(
                status='manual',
                updated_at=datetime.datetime.now(datetime.timezone.utc)
            )
        )

        postgres_coon.execute(op_meta_stmt, {'op_meta_id': op_meta_id})

    def file_flow_entry_point(
            self,
            records: List[Dict[str, Any]],
            start_stage: str,
            target_stage: str,
            tag_name: str,
            extract_method: str = 'netmind',
            priority: str = '1',
            source_type: str = None,
            tags_extend: List[str] = None
    ) -> Tuple[bool, Any, str]:
        """
        将一批文件记录写入处理队列，构建对应的元数据、步骤信息和附件信息。

        该方法会对传入参数进行校验，过滤已存在的记录，并按批次将数据写入队列中。

        :param records: 待处理的文件记录列表，每个记录是一个字典，必须包含唯一的 'id' 字段。
        :type records: List[Dict[str, Any]]
        :param start_stage: 文件处理流程的起始阶段。
        :type start_stage: str
        :param target_stage: 文件处理流程的目标阶段。
        :type target_stage: str
        :param tag_name: 标签名称，用于标识任务或处理流。
        :type tag_name: str
        :param extract_method: 提取方式，默认为 'netmind'，可根据具体业务自定义。
        :type extract_method: str, optional
        :param priority: 任务优先级，默认为 '1'，数值越小优先级越高。
        :type priority: str, optional
        :param source_type: 数据来源类型，默认为空字符串。
        :type source_type: str, optional

        :return: 包含三个元素的元组：
                 - 第一个元素表示是否成功（True/False）；
                 - 第二个元素为已存在记录的 ID 列表（或空字符串）；
                 - 第三个元素为提示信息或错误信息。
        :rtype: Tuple[bool, Any, str]
        """

        params = {
            'start_stage': start_stage,
            'target_stage': target_stage,
            'tag_name': tag_name,
            'extract_method': extract_method,
            'priority': priority,
            'current_stage': start_stage,
            'source_type': source_type,
            'tags_extend': tags_extend
        }

        is_valid, msg = self._validate_params(params)
        if not is_valid:
            return False, "", msg

        if isinstance(records, dict):
            records = [records]
        elif not isinstance(records, list):
            raise ValueError("records must be a dict or list of dicts.")

        is_valid, existing_ids, msg = self._check_records(records)
        if not is_valid:
            return False, existing_ids, msg
        logger.info(msg)

        batch_size = 1000
        attachments_batch, meta_batch, step_batch = [], [], []

        count = 0
        for record in records:
            if record['id'] in existing_ids:
                continue

            attachments, meta, step = self._build_insert_data(record, params)
            attachments_batch.extend(attachments)
            meta_batch.append(meta)
            step_batch.append(step)
            count += 1

            if len(meta_batch) >= batch_size:
                self._insert_data_to_queue([
                    {'table': self.table_op_attachment, 'data': attachments_batch},
                    {'table': self.table_op_meta, 'data': meta_batch},
                    {'table': self.table_op_step, 'data': step_batch}
                ])
                attachments_batch.clear()
                meta_batch.clear()
                step_batch.clear()

        # Insert remaining data
        if meta_batch:
            self._insert_data_to_queue([
                {'table': self.table_op_attachment, 'data': attachments_batch},
                {'table': self.table_op_meta, 'data': meta_batch},
                {'table': self.table_op_step, 'data': step_batch}
            ])

        return True, "", f"Data successfully queued. inserted_count: {count}"

    def file_flow_exit_point(
            self,
            limit_size: int = 1000,
            filters: Optional[Dict[str, Any]] = None,
            order_by: Optional[str] = None,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        从 op_meta 表中读取数据，支持分页、过滤和排序。

        :param limit_size: 每次返回的数据条数
        :param filters: 查询过滤条件，如 {'status': 'init'}
        :param order_by: 排序字段，如 'created_at desc'
        :param offset: 跳过的行数（分页偏移）
        :return: 查询结果列表，每项为 dict
        """
        stmt = select(self.table_op_meta)

        if filters:
            conditions = []
            for key, value in filters.items():
                column = getattr(self.table_op_meta.c, key, None)
                if column is not None:
                    if key == 'tags' and isinstance(value, str):
                        conditions.append(column.any(value))
                    else:
                        conditions.append(column == value)
            if conditions:
                stmt = stmt.where(and_(*conditions))

        if order_by:
            field_parts = order_by.strip().split()
            field_name = field_parts[0]
            sort_dir = field_parts[1].lower() if len(field_parts) > 1 else 'asc'

            column = getattr(self.table_op_meta.c, field_name, None)
            if column is not None:
                stmt = stmt.order_by(asc(column) if sort_dir == 'asc' else desc(column))

        stmt = stmt.offset(offset).limit(limit_size)

        with self.session_scope() as session:
            result = session.execute(stmt)
            rows = result.fetchall()

            for row in rows:
                yield dict(row._mapping)
                try:
                    op_meta_id = row.id
                    status = row.status
                    if status == 'success':
                        self._delete_and_backup_data_from_queue(session, op_meta_id)
                    elif status == 'failed':
                        self._update_failed_record_to_manual(session, op_meta_id)
                    else:
                        logger.info(f"Data is still processing. Current status: {status}")
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e



if __name__ == '__main__':
    file_flow = FileFlowHandle()

    # # 读取用例
    # filters = {
    #     'status': 'success',
    #     'tags': 'test_data'
    # }
    # limit_size = 4
    # result = file_flow.file_flow_exit_point(filters=filters, order_by='id asc', limit_size=limit_size)
    # count = 0
    # for data in result:
    #     count += 1
    #     print(data)
    #     if count >= 2:
    #         raise Exception('aaaa')


    # # 插入用例
    # records = [{"id": "test_id3", "s3_path_info": [{"store_path": "s3://orbit-common-resources/fyx_test/FC060083175_20150115.pdf", "file_name": "test_file_name"}]}]
    # start_stage = "convert"
    # target_stage = "embedding"
    # tag_name = "test_data"
    # priority = "4"
    # data_source = "test_data"
    # for i in range(10):
    #     records[0]['id'] = f"test_id{i}"
    #     status, ids, message = file_flow.file_flow_entry_point(records, start_stage, target_stage, tag_name)
    #     print(f"Status: {status}, IDs: {ids}, Message: {message}")
