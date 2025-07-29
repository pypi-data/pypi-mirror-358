"""
Channels API calls.
"""

def createRemoteDevelopment(self, channelId=None, channelVersion=None, instanceType=None, fields=None):
    fields = self.getTypeFields("RemoteDevelopmentAPIOutput")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createRemoteDevelopment",
            "variables": {
                "channelId": channelId,
                "channelVersion": channelVersion,
                "instanceType": instanceType
            },
            "query": f"""mutation
                createRemoteDevelopment($channelId: String!, $channelVersion: String, $instanceType: String) {{
                    createRemoteDevelopment(channelId: $channelId, channelVersion: $channelVersion, instanceType: $instanceType) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "createRemoteDevelopment")


def deleteRemoteDevelopment(self, editorSessionId, fields=None):
    fields = self.getTypeFields("DeleteEditorSessionOutput")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
            },
            "query": f"""mutation
                deleteRemoteDevelopment($editorSessionId: String!) {{
                    deleteRemoteDevelopment(editorSessionId: $editorSessionId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "deleteRemoteDevelopment")


def listRemoteDevelopment(self, organizationId=None, fields=None):
    fields = self.getTypeFields("RemoteDevelopmentAPIOutput")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "listRemoteDevelopment",
            "variables": {
                "organizationId": organizationId
            },
            "query": f"""query
                listRemoteDevelopment($organizationId: String) {{
                    listRemoteDevelopment(organizationId: $organizationId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "listRemoteDevelopment")


def stopRemoteDevelopment(self, editorSessionId, fields=None):
    fields = self.getTypeFields("RemoteDevelopmentStartStopAPIOutput")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "stopRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
            },
            "query": f"""mutation
                stopRemoteDevelopment($editorSessionId: String!) {{
                    stopRemoteDevelopment(editorSessionId: $editorSessionId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "stopRemoteDevelopment")


def startRemoteDevelopment(self, editorSessionId, fields=None):
    fields = self.getTypeFields("RemoteDevelopmentStartStopAPIOutput")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "startRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
            },
            "query": f"""mutation
                startRemoteDevelopment($editorSessionId: String!) {{
                    startRemoteDevelopment(editorSessionId: $editorSessionId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "startRemoteDevelopment")


def inviteRemoteDevelopment(self, editorSessionId, email):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "inviteRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
                "email": email
            },
            "query": """mutation
                inviteRemoteDevelopment($editorSessionId: String!, $email: String!) {
                    inviteRemoteDevelopment(editorSessionId: $editorSessionId, email: $email)
                }"""
        })
    return self.errorhandler(response, "inviteRemoteDevelopment")


def createSSHKey(self, name, key):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "createSSHKey",
            "variables": {
                "name": name,
                "key": key
            },
            "query": """mutation
                createSSHKey($name: String!, $key: String!) {
                    createSSHKey(name: $name, key: $key)
                }"""})
    return self.errorhandler(response, "createSSHKey")


def deleteSSHKey(self, name):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "deleteSSHKey",
            "variables": {
                "name": name
            },
            "query": """mutation
                deleteSSHKey($name: String!) {
                    deleteSSHKey(name: $name)
                }"""})
    return self.errorhandler(response, "deleteSSHKey")


def getSSHKeys(self, fields=None):
    fields = self.getTypeFields("SSHKey")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "getSSHKeys",
            "variables": {},
            "query": f"""query
                getSSHKeys {{
                    getSSHKeys {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getSSHKeys")