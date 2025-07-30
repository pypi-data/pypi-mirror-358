from pydantic import BaseModel


class ApiConfig(BaseModel):
    api_key: str
    environment: str

    def get_base_url(self):
        if self.environment == 'sandbox':
            return 'https://sandbox-api.alegra.com/e-provider/col/v1'
        elif self.environment == 'production':
            return 'https://api.alegra.com/e-provider/col/v1'
        else:
            raise ValueError("Invalid environment. Choose 'sandbox' or 'production'.")
