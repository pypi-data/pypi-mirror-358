# from database_mysql_local.connector import Connector
from database_mysql_local.generic_crud_mysql import GenericCrudMysql
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.LoggerLocal import Logger
from logger_local.MetaLogger import MetaLogger
from mysql.connector.errors import IntegrityError  # noqa
from .token__user_external import TokenUserExternals
import mysql.connector


USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 115
USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "user_external_local_python"
DEVELOPER_EMAIL = "idan.a@circ.zone"
object_init = {
    "component_id": USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    "component_name": USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL,
}

USER_EXTERNAL_SCHEMA_NAME = "user_external"
USER_EXTERNAL_TABLE_NAME = "user_external_table"
USER_EXTERNAL_VIEW_NAME = "user_external_view"
USER_EXTERNAL_ID_COLUMN_NAME = "user_external_id"
TOKEN_USER_EXTERNAL_GENERAL_VIEW_NAME = "user_external_latest_token_general_view"

USER_EXTERNAL_PII_SCHEMA_NAME = "user_external_pii"
USER_EXTERNAL_PII_TABLE_NAME = "user_external_pii_table"
USER_EXTERNAL_PII_GENERAL_VIEW_NAME = "user_external_pii_general_view"
PASSWORD_CLEAR_TEXT_COLUMN_NAME = "password_clear_text"

logger = Logger.create_logger(object=object_init)



class UserExternalsLocal(GenericCrudMysql, metaclass=MetaLogger, object=object_init):
    def __init__(self, is_test_data: bool = False):
        super().__init__(
            default_schema_name=USER_EXTERNAL_SCHEMA_NAME,
            default_table_name=USER_EXTERNAL_TABLE_NAME,
            default_view_table_name=USER_EXTERNAL_VIEW_NAME,
            default_column_name=USER_EXTERNAL_ID_COLUMN_NAME,
            is_test_data=is_test_data,
        )
        self.token__user_externals = TokenUserExternals(
            is_test_data=is_test_data,
        )

        self.user_external_pii = GenericCrudMysql(
            default_schema_name=USER_EXTERNAL_PII_SCHEMA_NAME,
            default_table_name=USER_EXTERNAL_PII_TABLE_NAME,
            default_view_table_name=USER_EXTERNAL_PII_GENERAL_VIEW_NAME,
            default_column_name=PASSWORD_CLEAR_TEXT_COLUMN_NAME,
            is_test_data=is_test_data,
        )

    def insert(self, *, data_dict: dict = None, 
               ignore_duplicate: bool = False, 
               commit_changes: bool = True) -> int:
        
        if "main_profile_id" in data_dict and "system_id" in data_dict and "username" in data_dict:
            get_query = 'SELECT * ' \
                       f'FROM `{USER_EXTERNAL_SCHEMA_NAME}`.`{USER_EXTERNAL_TABLE_NAME}` ' \
                       f'WHERE main_profile_id={data_dict["main_profile_id"]} ' \
                       f'AND system_id={data_dict["system_id"]} ' \
                       f'AND username=\"{data_dict["username"]}\"' 
            self.cursor.execute(get_query)
            retrieved_data = self.cursor.fetchall()
            if len(retrieved_data) > 0:
                raise IntegrityError(msg="Entry with this profile_id, system_id, and username already exists in database")
        
        return super().insert(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            table_name=USER_EXTERNAL_TABLE_NAME,
            data_dict=data_dict, ignore_duplicate=ignore_duplicate,
            commit_changes=commit_changes
            )

    def get_password_clear_text_by_system_id_and_profile_id(
            self,
            system_id: int,
            profile_id: int
    ) -> str | None:
        
        object_start = {"system_id":system_id, "profile_id":profile_id}
        logger.start(object=object_start)
        
        self.cursor.execute(sql_statement="SELECT password_clear_text " \
                            "FROM user_external_pii.user_external_pii_view " \
                            "JOIN user_external.user_external_view " \
                            "ON user_external_pii.user_external_pii_view.user_external_id = user_external.user_external_view.user_external_id " \
                            f"WHERE user_external.user_external_view.system_id={system_id} AND main_profile_id={profile_id}"
                            )
        password = self.cursor.fetchall()
        if (len(password) > 1):
            raise mysql.connector.errors.InternalError("More than one entry for given system_id and profile_id")
        elif len(password) == 0:
            return None
        return password[0][0]
    
    def get_password_clear_text_by_system_id_profile_id_username(
            self,
            system_id: int,
            profile_id: int,
            username: str,
    ) -> str | None:
        
        object_start = {"system_id":system_id, "profile_id":profile_id}
        logger.start(object=object_start)
        
        self.cursor.execute(sql_statement="SELECT password_clear_text " \
                            "FROM user_external_pii.user_external_pii_view " \
                            "JOIN user_external.user_external_view " \
                            "ON user_external_pii.user_external_pii_view.user_external_id = user_external.user_external_view.user_external_id " \
                            f"WHERE user_external.user_external_view.system_id={system_id} AND main_profile_id={profile_id} AND username=\'{username}\'"
                            )
        password = self.cursor.fetchall()
        if len(password) == 0:
            return None
        password_clear_text = password[0][0]
        return password_clear_text


    # TODO When creating a new user-external should add url to the person_url (otherwise profile_url).
    # TODO Shall we rename insert_or_update... to upsert...
    # TODO Do we have the same method name in both classes? - Shall we?
    def insert_or_update_user_external_access_token(
        self,
        *,
        profile_id: int,
        system_id: int,
        username: str,
        refresh_token: str = None,
        access_token: str,
        expiry=None,
    ) -> int:
        object_start = {  # noqa
            "main.profile_id": profile_id,
            "system_id": system_id,
            "username": username,
            "refresh_token": refresh_token,
            "access_token": access_token,
            "expiry": expiry,
        }
        logger.start(object=object_start)

        current_access_token = self.get_access_token(
            system_id=system_id, username=username, profile_id=profile_id
        )
        if current_access_token is not None:
            self.delete_access_token(
                system_id=system_id, username=username, profile_id=profile_id
            )

        user_external_id = self.select_one_value_by_column_and_value(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=USER_EXTERNAL_VIEW_NAME,
            select_clause_value=USER_EXTERNAL_ID_COLUMN_NAME,
            column_name="username",
            column_value=username,
        )

        if user_external_id is None:

            data_dict_user_external = {
                "system_id": system_id,
                "username": username,
                "main_profile_id": profile_id,
                "refresh_token": refresh_token,
            }

            data_dict_user_external_compare = {
                "system_id": system_id,
                "username": username,
                "main_profile_id": profile_id,
            }

            user_external_id_new = self.upsert(
                data_dict=data_dict_user_external,
                data_dict_compare=data_dict_user_external_compare,
            )
        else:
            user_external_id_new = user_external_id

        # TODO Why ()
        token__user_external_id = (
            self.token__user_externals.insert_or_update_user_external_access_token(
                user_external_id=user_external_id_new,
                username=username,
                profile_id=profile_id,
                access_token=access_token,
                expiry=expiry,
            )
        )
        logger.info(
            log_message=f"user_external_access_token inserted/updated, access_token_row_id: {token__user_external_id}",
        )

        user_external_updated_inserted_id = self.select_one_value_by_column_and_value(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=TOKEN_USER_EXTERNAL_GENERAL_VIEW_NAME,
            select_clause_value=USER_EXTERNAL_ID_COLUMN_NAME,
            column_name="access_token",
            column_value=access_token,
        )

        return user_external_updated_inserted_id

    # TODO Shall we default the profile_id to profile_id from User Context?
    # TODO Why we have two methods which look. very similar?
    # TODO get_access_token_by_user_external_id() or get_access_token_by_profile_id_system_id_user_id(), shall we have two methods?
    def get_access_token(
        self,
        *,
        user_external_id: int | None = None,
        system_id: int,
        username: str,
        profile_id: int = None,
    ) -> str:
        object_start = {  # noqa
            "username": username,
            "profile_id": profile_id,
            "system_id": system_id,
        }
        logger.start(object=object_start)

        if user_external_id:
            access_token = self.token__user_externals.get_access_token(
                user_external_id=user_external_id,
            )
            return access_token

        if profile_id is None:
            access_token = (
                self.token__user_externals.get_access_token_by_username_and_system_id(
                    username=username,
                    system_id=system_id,
                )
            )
            return access_token

        access_token = self.token__user_externals.get_access_token_by_username_system_id_and_profile_id(
            username=username,
            system_id=system_id,
            profile_id=profile_id,
        )

        return access_token

    def get_access_token_by_username_and_system_id(
        self, *, username: str, system_id: int
    ) -> str:
        return self.get_access_token(
            username=username, system_id=system_id, profile_id=None
        )



    def update_user_external_access_token(
        self,
        *,
        user_external_id: int,
        system_id: int,
        username: str,
        profile_id: int,
        access_token,
        expiry=None,
    ) -> int:
        """
        Updates the access token for a given user_external_id, if user_external_id is None, it will
        get the user_external_id by system_id and profile_id

        Keyword arguments:
        argument --

        - user_external_id: int - the user_external_id
        - system_id: int - the system id
        - username: str - the username/email
        - profile_id: int - the profile id
        - access_token: str - the new access token
        - expiry: str - the new expiry date

        Return: int - the user_external_id of the updated access token
        """

        object_start = {  # noqa
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
            "access_token": access_token,
        }
        logger.start(object=object_start)

        if user_external_id is None:
            user_external_id = self.__get_user_external_id_by_system_id_and_profile_id(
                system_id=system_id, profile_id=profile_id
            )

        updated_rows = self.token__user_externals.update_access_token(
            user_external_id=user_external_id,
            name=username,
            access_token=access_token,
            expiry=expiry,
        )
        logger.info(
            log_message=f"user_external_access_token updated, updated_rows: {updated_rows}",
        )

        updated_user_external_id = user_external_id

        return updated_user_external_id

    def update_refresh_token_by_user_external_id(
        self, *, user_external_id: int, refresh_token: str
    ) -> int:
        """
        Updates the refresh token for a given user_external_id

        Keyword arguments:
        arguments:

        user_external_id: int - the user_external_id
        refresh_token: str - the new refresh token


        Return: int - the number of rows updated
        """

        object_start = {"user_external_id": user_external_id, "refresh_token": refresh_token}
        logger.start(object=object_start)

        data_dict = {
            "refresh_token": refresh_token,
        }

        updated_rows = self.update_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            table_name=USER_EXTERNAL_TABLE_NAME,
            where=f"{USER_EXTERNAL_ID_COLUMN_NAME}=%s",
            params=(user_external_id,),
            data_dict=data_dict,
        )

        logger.info(
            log_message=f"user_external_refresh_token updated, updated_rows: {updated_rows}",
        )

        return updated_rows

    def update_is_refresh_token_valid_status_by_refresh_token(
        self, *, refresh_token: str, is_refresh_token_valid: bool
    ) -> int:
        """
        Updates the is_refresh_token_valid status for a given refresh_token

        Keyword arguments:
        arguments:

        refresh_token: str - the refresh token
        is_refresh_token_valid: bool - the new is_refresh_token_valid status


        Return: int - the number of rows updated
        """

        object_start = {
            "refresh_token": refresh_token,
            "is_refresh_token_valid": is_refresh_token_valid,
        }
        logger.start(object=object_start)

        data_dict = {
            "is_refresh_token_valid": is_refresh_token_valid,
        }

        updated_rows = self.update_by_column_and_value(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            table_name=USER_EXTERNAL_TABLE_NAME,
            column_name="refresh_token",
            column_value=refresh_token,
            data_dict=data_dict,
        )

        logger.info(
            log_message=f"user_external_is_refresh_token_valid updated, updated_rows: {updated_rows}",
        )

        return updated_rows

    def delete_access_token(
        self, *, system_id: int, username: str, profile_id: int
    ) -> int:
        object_start = {
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
        }
        logger.start(object=object_start)

        user_external_id = self.__get_user_external_id_by_system_id_and_profile_id(
            system_id=system_id, profile_id=profile_id
        )

        deleted_rows = (
            self.token__user_externals.delete_access_token_by_user_external_id(
                user_external_id=user_external_id,
                username=username,
            )
        )
        return deleted_rows

    def get_auth_details(
        self, *, system_id: int, username: str, profile_id: int
    ) -> dict:
        """
        Gets authentication details including access_token, refresh_token, and expiry

        Keyword arguments:
        system_id: int - the system id
        username: str - the username/email
        profile_id: int - the profile id

        Return: dict - a dictionary containing user_external_id, access_token, refresh_token, expiry, is_refresh_token_valid, and oauth_state
        """

        logger.deprecation_warning(old_name="get_auth_details",
                                   new_name="get_auth_details_by_profile_id_system_id_username",
                                   )

        auth_details = None
        object_start = {
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
        }
        logger.start(object=object_start)

        user_external_id = self.__get_user_external_id_by_system_id_and_profile_id(
            system_id=system_id, profile_id=profile_id
        )

        auth_details = self.token__user_externals.get_auth_details(
            user_external_id=user_external_id,
        )

        return auth_details

    def get_auth_details_by_profile_id_system_id_username(
        self, *, system_id: int, username: str, profile_id: int
    ) -> dict:
        """
        Gets authentication details including access_token, refresh_token, and expiry

        Keyword arguments:
        system_id: int - the system id
        username: str - the username/email
        profile_id: int - the profile id

        Return: dict - a dictionary containing user_external_id, access_token, refresh_token, expiry, is_refresh_token_valid, and oauth_state
        """

        auth_details = None
        object_start = {
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
        }
        logger.start(object=object_start)

        user_external_id = self.__get_user_external_id_by_profile_id_system_id_username(
            system_id=system_id, profile_id=profile_id, username=username
        )

        auth_details = self.token__user_externals.get_auth_details(
            user_external_id=user_external_id,
        )

        return auth_details

    # Might have multiple users in the same profle_id_system_id
    # TODO get_auth_details_by_profile_id_system_id_user_id()
    def get_auth_details_by_system_id_and_profile_id(
        self, *, system_id: int, profile_id: int
    ) -> dict:
        """
        Gets authentication details including access_token, refresh_token, and expiry

        Keyword arguments:
        system_id: int - the system id
        profile_id: int - the profile id

        Return: dict - a dictionary containing user_external_id, access_token, refresh_token, expiry, is_refresh_token_valid, and oauth_state
        """

        object_start = {"system_id": system_id, "profile_id": profile_id}  # noqa
        logger.start(object=object_start)

        try:
            auth_details = (
                self.token__user_externals.get_auth_details_by_system_id_and_profile_id(
                    system_id=system_id,
                    profile_id=profile_id,
                )
            )

        except Exception as e:
            logger.error(
                log_message="Error getting auth_details",
                object={
                    "system_id": system_id,
                    "profile_id": profile_id,
                    "error": str(e),
                },
            )
            raise e
        return auth_details

    def get_credential_storage_id_by_system_id_and_profile_id(
        self, *, system_id: int, profile_id: int
    ):
        credential_storage_id = self.select_one_value_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=USER_EXTERNAL_VIEW_NAME,
            select_clause_value="credential_storage_id",
            where="system_id=%s AND main_profile_id=%s",
            params=(system_id, profile_id),
        )

        return credential_storage_id

    # A profile can have multiple user_external_id in the same system
    # TODO We should rename to get_external_user_ids_by_profile_id_system_id() it should be backward compatible
    def __get_user_external_id_by_system_id_and_profile_id(
        self, *, system_id: int, profile_id: int
    ):
        # TODO not select_one, select_multi
        user_external_id = self.select_one_value_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=USER_EXTERNAL_VIEW_NAME,
            select_clause_value=USER_EXTERNAL_ID_COLUMN_NAME,
            where="main_profile_id=%s AND system_id=%s",
            params=(profile_id, system_id),
            order_by="updated_timestamp DESC",
        )

        return user_external_id

    def __get_user_external_id_by_profile_id_system_id_username(
        self, *, profile_id: int, system_id: int, username: str
    ):
        user_external_id = self.select_one_value_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=USER_EXTERNAL_VIEW_NAME,
            select_clause_value=USER_EXTERNAL_ID_COLUMN_NAME,
            where="main_profile_id=%s AND system_id=%s AND username=%s",
            params=(profile_id, system_id, username),
            order_by="updated_timestamp DESC",
        )

        return user_external_id
    
    def get_user_external_id_by_profile_id_system_id_username(
        self, *, profile_id: int, system_id: int, username: str
    ):
        user_external_id = self.select_one_value_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=USER_EXTERNAL_VIEW_NAME,
            select_clause_value=USER_EXTERNAL_ID_COLUMN_NAME,
            where="main_profile_id=%s AND system_id=%s AND username=%s",
            params=(profile_id, system_id, username),
            order_by="updated_timestamp DESC",
        )

        return user_external_id

    @staticmethod
    def get_recipient_user_dict(where: str) -> dict:
        # Return all the usernames and ids that the recipient has
        user_external_generic_crud = GenericCrudMysql(default_schema_name="user_external")

        username = user_external_generic_crud.select_multi_value_by_where(
            schema_name="user_external",
            view_table_name="user_external_general_view",
            select_clause_value="username",
            where=where,
        )
        user_external_id = user_external_generic_crud.select_multi_value_by_where(
            schema_name="user_external",
            view_table_name="user_external_general_view",
            select_clause_value="user_external_id",
            where=where,
        )
        telephone_number = user_external_generic_crud.select_multi_value_by_where(
            schema_name="user_external",
            view_table_name="user_external_general_view",
            select_clause_value="phone.full_number_normalized",
            where=where,
        )

        user_dict = {
            "username": list(username),
            "user_external_id": list(user_external_id),
            "phone.full_number_normalized": list(telephone_number),
        }
        return user_dict
