# ICS to SMS

Can be used from command line, I like [passwordstore](https://www.passwordstore.org/) so I'd use:

    python ics_to_sms.py --ics-url 'https://framagenda.org/.../?export' --ics-username mdk --ics-password "$(pass framagenda)" --free-user "$(pass free/sms-api-id)" --free-api-key "$(pass free/sms-api-key)"


It can also be configured using a toml file like:

    python ics_to_sms.py --config config.toml

with `config.toml` containing:

```toml
ics_url = "https://..."
ics_username = "mdk"
ics_passwordstore = "redacted for my privacy"
free_user = "..."
free_api_key = "..."
```
