import brevo_python


class BrevoAPI:
    def __init__(self, api_key: str):
        configuration = brevo_python.Configuration()
        configuration.api_key["api_key"] = api_key

        client = brevo_python.ApiClient(configuration)

        self.Account = brevo_python.AccountApi(client)
        self.Companies = brevo_python.CompaniesApi(client)
        self.Contacts = brevo_python.ContactsApi(client)
        self.Conversations = brevo_python.ConversationsApi(client)
        self.Coupons = brevo_python.CouponsApi(client)
        self.Deals = brevo_python.DealsApi(client)
        self.Domains = brevo_python.DomainsApi(client)
        self.Ecommerce = brevo_python.EcommerceApi(client)
        self.EmailCampaigns = brevo_python.EmailCampaignsApi(client)
        self.Events = brevo_python.EventsApi(client)
        self.ExternalFeeds = brevo_python.ExternalFeedsApi(client)
        self.Files = brevo_python.FilesApi(client)
        self.InboundParsing = brevo_python.InboundParsingApi(client)
        self.MasterAccount = brevo_python.MasterAccountApi(client)
        self.Notes = brevo_python.NotesApi(client)
        self.Payments = brevo_python.PaymentsApi(client)
        self.Process = brevo_python.ProcessApi(client)
        self.Reseller = brevo_python.ResellerApi(client)
        self.SMSCampaigns = brevo_python.SMSCampaignsApi(client)
        self.Senders = brevo_python.SendersApi(client)
        self.Tasks = brevo_python.TasksApi(client)
        self.TransactionalSMS = brevo_python.TransactionalSMSApi(client)
        self.TransactionalWhatsApp = brevo_python.TransactionalWhatsAppApi(client)
        self.TransactionalEmails = brevo_python.TransactionalEmailsApi(client)
        self.User = brevo_python.UserApi(client)
        self.Webhooks = brevo_python.WebhooksApi(client)
        self.WhatsAppCampaigns = brevo_python.WhatsAppCampaignsApi(client)
