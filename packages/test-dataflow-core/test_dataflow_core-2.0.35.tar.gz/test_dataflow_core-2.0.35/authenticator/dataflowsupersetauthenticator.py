from flask import redirect, request, jsonify
from flask_appbuilder.security.views import AuthDBView
from flask_appbuilder.security.views import expose
from flask_login import login_user
from flask_jwt_extended import (
    create_access_token
)
from flask_appbuilder.const import (
    API_SECURITY_ACCESS_TOKEN_KEY
)
from superset.security import SupersetSecurityManager
from dataflow.dataflow import Dataflow

class DataflowAuthDBView(AuthDBView):
    def __init__(self):
        self.dataflow = Dataflow()

    @expose('/login/', methods=['GET'])
    def login_redirect(self):
        try:
            session_id = request.cookies.get('dataflow_session')
            
            user_details = self.dataflow.auth(session_id)
            user = self.appbuilder.sm.find_user(username=user_details['user_name'])
            if user:
                login_user(user, remember=False)
            else:
                user = self.appbuilder.sm.add_user(
                    username=user_details['user_name'], 
                    first_name=user_details.get("first_name", ""),
                    last_name=user_details.get("last_name", ""), 
                    email=user_details.get("email", ""), 
                    role=self.appbuilder.sm.find_role('Admin')
                )
                if user:
                    login_user(user, remember=False)
                    
            return redirect(self.appbuilder.get_url_for_index)

        except Exception as e:
            return super().login()

    @expose("/login", methods=["POST"])
    def login_token(self):
        login_payload = request.get_json()
        user = self.appbuilder.sm.find_user(username=login_payload["user_name"])

        if not user:
            user = self.appbuilder.sm.add_user(
                username=login_payload["user_name"], 
                first_name=login_payload.get("first_name", ""),
                last_name=login_payload.get("last_name", ""), 
                email=login_payload.get("email", ""), 
                role=self.appbuilder.sm.find_role('Admin')
            )
        
        resp = dict()
        resp[API_SECURITY_ACCESS_TOKEN_KEY] = create_access_token(
            identity=str(user.id), fresh=True
        )
        return jsonify(resp)
    
class DataflowSecurityManager(SupersetSecurityManager):
    authdbview = DataflowAuthDBView
    def __init__(self, appbuilder):
        super(DataflowSecurityManager, self).__init__(appbuilder)