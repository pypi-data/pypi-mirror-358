import requests as req

## DISCLAIMER:
##      Some features can rate limit your account, use this at your own risk.


class Client:
    def __init__(self, token: str):
        self.token = token
        self.uri = "https://discord.com/api/v10"

    def _headers(self):
        return {"Authorization": self.token}

    def get_dms(self):
        url = f"{self.uri}/users/@me/channels"
        res = req.get(url, headers=self._headers())

        if res.status_code == 200:
            return [
                (recipient["id"], recipient["username"])
                for channel in res.json()
                for recipient in channel.get("recipients", [])
            ]
        return []

    def get_country(self):
        url = f"{self.uri}/users/@me/billing/country-code"
        res = req.get(url, headers=self._headers())

        if res.status_code == 200:
            return res.json().get("country_code")
        return None

    def get_guilds(self):
        url = f"{self.uri}/users/@me/guilds"
        res = req.get(url, headers=self._headers())

        if res.status_code == 200:
            return [(g["id"], g["name"]) for g in res.json()]
        return []

    def get_friends(self):
        url = f"{self.uri}/users/@me/relationships"
        res = req.get(url, headers=self._headers())

        if res.status_code == 200:
            return [
                (f["id"], f["user"]["username"])
                for f in res.json()
            ]
        return []

    def token_lookup(self):
        api_v6 = "https://discordapp.com/api/v6"
        user_url = f"{api_v6}/users/@me"
        billing_url = f"{api_v6}/users/@me/billing/payment-sources"

        res = req.get(user_url, headers=self._headers())
        if res.status_code != 200:
            return None

        profile = res.json()

        result = {
            "username": profile["username"],
            "user_id": profile["id"],
            "email": profile.get("email"),
            "phone": profile.get("phone"),
            "flags": profile.get("flags"),
            "locale": profile.get("locale"),
            "mfa_enabled": profile.get("mfa_enabled"),
            "premium_type": profile.get("premium_type"),
            "valid_payments": 0,
            "payment_types": []
        }

        try:
            payment_res = req.get(billing_url, headers=self._headers())
            payment_res.raise_for_status()
            for p in payment_res.json():
                if not p.get("invalid", True):
                    if p["type"] == 1:
                        result["payment_types"].append("CreditCard")
                    elif p["type"] == 2:
                        result["payment_types"].append("PayPal")
                    result["valid_payments"] += 1
        except req.RequestException:
            pass

        return result

    def send_message(self, channel_id, message):
        url = f"{self.uri}/channels/{channel_id}/messages"
        data = {"content": message, "tts": False}
        res = req.post(url, headers=self._headers(), json=data)
        return res.status_code == 200

    def remove_friend(self, user_id):
        url = f"{self.uri}/users/@me/relationships/{user_id}"
        res = req.delete(url, headers=self._headers())
        return res.status_code == 204

    def set_language(self, country_code):
        valid_codes = [
            'da', 'de', 'en-GB', 'en-US', 'es-ES', 'fr', 'hr', 'it',
            'lt', 'hu', 'nl', 'no', 'pl', 'pt-BR', 'ro', 'fi', 'sv-SE',
            'vi', 'tr', 'cs', 'el', 'bg', 'ru', 'uk', 'th', 'zh-CN',
            'ja', 'ko'
        ]
        if country_code not in valid_codes:
            return False

        url = f"{self.uri}/users/@me/settings"
        res = req.patch(url, headers=self._headers(), json={"locale": country_code})
        return res.status_code == 200

    def set_hypesquad(self, house_id):
        url = f"{self.uri}/hypesquad/online"
        res = req.post(url, headers=self._headers(), json={"house_id": house_id})
        return res.status_code == 204

    def block_user(self, user_id):
        url = f"{self.uri}/users/@me/relationships/{user_id}"
        res = req.put(url, headers=self._headers(), json={"type": 2})
        return res.status_code == 204

    def unblock_user(self, user_id):
        url = f"{self.uri}/users/@me/relationships/{user_id}"
        res = req.delete(url, headers=self._headers())
        return res.status_code == 204

    def get_messages(self, channel_id):
        url = f"{self.uri}/channels/{channel_id}/messages"
        res = req.get(url, headers=self._headers())
        if res.status_code != 200:
            return []

        result = []
        for msg in res.json():
            entry = {
                "message_id": msg["id"],
                "username": msg["author"]["username"],
                "content": msg["content"],
                "attachments": [a["url"] for a in msg.get("attachments", [])],
                "embeds": []
            }
            for embed in msg.get("embeds", []):
                if 'url' in embed:
                    entry["embeds"].append(embed["url"])
                if 'image' in embed and 'url' in embed['image']:
                    entry["embeds"].append(embed['image']['url'])
            result.append(entry)
        return result
