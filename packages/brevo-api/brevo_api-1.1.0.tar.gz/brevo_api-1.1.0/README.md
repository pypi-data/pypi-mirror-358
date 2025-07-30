# Brevo API Wrapper

[![Python](https://img.shields.io/pypi/pyversions/brevo-api.svg)](https://badge.fury.io/py/brevo-api)
[![PyPI](https://badge.fury.io/py/brevo-api.svg)](https://badge.fury.io/py/brevo-api)
[![PyPI](https://github.com/ChemicalLuck/brevo-api/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ChemicalLuck/brevo-api/actions/workflows/python-publish.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/brevo-api)

## Installation

```bash
pip install brevo-api
```

## Usage

```python
from brevo import BrevoAPI

client = BrevoAPI(api_key='YOUR_API_KEY', partner_key='YOUR_PARTNER_KEY')

response = client.Account.get_account()
print(response)
```

For more details on the content of the reponses, visit the [generate python SDK by Brevo](https://github.com/getbrevo/brevo-python).

## Resources Available

- AccountApi
- CompaniesApi
- ContactsApi
- ConversationsApi
- CouponsApi
- DealsApi
- DomainsApi
- EcommerceApi
- EmailCampaignsApi
- EventsApi
- ExternalFeedsApi
- FilesApi
- InboundParsingApi
- MasterAccountApi
- NotesApi
- PaymentsApi
- ProcessApi
- ResellerApi
- SMSCampaignsApi
- SendersApi
- TasksApi
- TransactionalSMSApi
- TransactionalWhatsAppApi
- TransactionalEmailsApi
- UserApi
- WebhooksApi
- WhatsAppCampaignsApi

## License

[MIT](LICENSE)

## Acknowledgements

This project is a wrapper of brevo_python by getbrevo.
