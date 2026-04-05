from typing import Dict, Any, List

class MockTools:
    """Registry of mock tools that return deterministic safe responses."""

    @staticmethod
    def process_payment(amount: float, recipient: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "amount": amount, "recipient": recipient, "message": "Payment processed (mock)"}

    @staticmethod
    def send_email(recipient: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "recipient": recipient, "subject": subject, "message": "Email sent (mock)"}

    @staticmethod
    def read_file(path: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "path": path, "content": "mock file content"}

    @staticmethod
    def write_file(path: str, content: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "path": path, "message": "File written (mock)"}

    @staticmethod
    def delete_file(path: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "path": path, "message": "File deleted (mock)"}

    @staticmethod
    def lookup_invoice(invoice_id: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "invoice_id": invoice_id, "amount": 247.50, "vendor": "CloudHost GmbH"}

    @staticmethod
    def add_user(username: str, role: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "username": username, "role": role, "message": "User added (mock)"}

    @staticmethod
    def execute_script(script: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "script": script, "message": "Script executed (mock)"}

    @staticmethod
    def wire_transfer(amount: float, account: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "amount": amount, "account": account, "message": "Wire transfer complete (mock)"}
    
    @staticmethod
    def update_payroll(account: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "account": account, "message": "Payroll updated (mock)"}
    
    @staticmethod
    def grant_access(user: str, level: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "user": user, "level": level, "message": "Access granted (mock)"}

    @staticmethod
    def execute_trade(symbol: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "symbol": symbol, "message": "Trade executed (mock)"}
    
    @staticmethod
    def export_doc(doc: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "doc": doc, "message": "Doc exported (mock)"}
    
    @staticmethod
    def log_event(message: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "message_logged": message, "message": "Event logged (mock)"}
        
    @staticmethod
    def approve_expense(threshold: float, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "threshold": threshold, "message": "Threshold updated (mock)"}

    @staticmethod
    def search(query: str, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "query": query, "results": ["mock result 1", "mock result 2"]}
        
    @classmethod
    def get_all_tool_names(cls) -> List[str]:
        return [func for func in dir(cls) if callable(getattr(cls, func)) and not func.startswith("__")]
