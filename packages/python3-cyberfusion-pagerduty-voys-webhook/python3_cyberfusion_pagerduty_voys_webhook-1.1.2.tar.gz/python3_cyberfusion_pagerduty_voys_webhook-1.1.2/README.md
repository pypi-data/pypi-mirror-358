# python3-cyberfusion-pagerduty-voys-webhook

Webhook server to dynamically route Voys calls to on-call PagerDuty users.

This webhook server is intended to route phone calls (handled by VoIP provider [Voys](https://www.voys.nl/)) to users that are on-call on [PagerDuty](https://www.pagerduty.com/) - without having to keep both in sync manually.

When using the webhook offered by this program in your Voys dial plan (see instructions under 'Configure'),
calls are routed to the phone number specified in the PagerDuty user's 'Notification Rules'.

If multiple PagerDuty users are on-call, calls are routed to a random user.
If the chosen PagerDuty user has multiple phone numbers, a random one is chosen.

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-pagerduty-voys-webhook

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

* Place your PagerDuty API key in `/etc/pagerduty-voys-webhook/api_key` (regular text file). See instructions under 'Configure'.
* Place a randomly generated secret key in `/etc/pagerduty-voys-webhook/secret_key` (regular text file). When calling the webhook, this key must be specified - as a security measure. For example, you can generate a random secret using `openssl`: `openssl rand -hex 32`
* Place the escalation policy ID in `/etc/pagerduty-voys-webhook/escalation_policy_id` (regular text file). Users to route calls to are retrieved from this escalation policy. For example, if you have a group of Customer Liaisons to route calls to, you can create a dedicated escalation policy for them.

# Usage

## Run

The webhook server runs on `:::5839`.

### Manually

Run the app using an ASGI server such as Uvicorn.

### systemd

    systemctl start pagerduty-voys-webhook-server.service

## SSL

Use a proxy that terminates SSL. E.g. [HAProxy](http://www.haproxy.org/).

### Example HAProxy config

```
frontend fr_ssl
  bind :::5840 v4v6 ssl crt /etc/ssl/certs/example_com.pem alpn h2,http/1.1 curves secp384r1:secp224r1
  mode http
  use_backend bk_pagerduty_voys_webhook_server

backend bk_pagerduty_voys_webhook_server
  mode http
  balance source
  server localhost ::1:5839 check
```

## Configure

### Create PagerDuty API key

* Log in to PagerDuty.
* Navigate to Integrations -> API Access Keys.
* Click 'Create New API Key'.
* For 'Description', fill in a free-form description.
* Tick 'Read-only API Key'.
* Click 'Create Key'.

### Add webhook in Voys Freedom

* Log in to Voys Freedom.
* Navigate to Admin -> Webhooks.
* Click 'Add'.
* For 'Name', fill in a free-form name.
* For 'Caller id forwarding', select whichever option suits your use case. This option controls which phone number the person sees who the call is routed to.
* Set 'URL template' to: the URL on which this program runs + `/voys-webhook?secret_key=` + secret key (from `/etc/pagerduty-voys-webhook/secret_key`). For example: `https://voys-webhook.example.com/voys-webhook?secret_key=r6cZPVkZdqujY6dME5uqDytK`

### Use webhook in dial plan

* Log in to Voys Freedom.
* Navigate to your dial plan.
* Click 'Edit dial plan'.
* Click 'add step'.
* Select your newly added webhook.
* In the 'HTTP and IVR success' branch, click 'Edit' next to 'Unfilled step'.
* Select 'Variable destination'.

Optionally, you can specify 'fallback' steps in the 'HTTP or IVR failed' branch. For example, if the specified secret key is invalid, or this program doesn't (properly) respond for any other reason.

For more information, see Voys' own documentation on <https://help.voys.nl/integraties-koppelingen-webhooks/webhooks>.

### (Optional) IP-restrict webhook request

This program returns phone numbers, which might be considered confidential/sensitive.

Although this program requires a secret key for webhook calls, it's recommended to restrict requests to Voys' IP addresses.

Find Voys' outgoing IP addresses here: <https://help.voys.nl/netwerk-trunk-videobellen-en-ata/firewall-instellen>
