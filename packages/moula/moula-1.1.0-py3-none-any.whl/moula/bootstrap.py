from the_conf import TheConf

metaconf = {
    "config_file_environ": ["CONFIG"],
    "config_files": ["~/.config/moula/moula.yml", "/etc/moula/moula.yml"],
    "parameters": [
        {"name": {"default": "moula"}},
        {
            "firefly": [
                {
                    "default_cash_account": {
                        "default": "",
                    }
                },
                {"url": {"required": True, "type": str}},
                {
                    "lookback": {
                        "required": True,
                        "default": 0,
                        "type": int,
                        "help_txt": "number of days to look into "
                        "when comparing with firefly data",
                    }
                },
                {"token": {"required": True}},
                {"push": {"required": True, "type": bool}},
            ],
        },
        {"merge_date_tolerance": {"type": int, "default": 1}},
        {"accuracy": {"type": int, "default": 2}},
        {
            "loop": [
                {"enabled": {"type": bool, "default": False}},
                {"interval": {"type": int, "default": 240}},
            ]
        },
        {
            "prometheus": [
                {"port": {"type": int, "default": 9100}},
                {"namespace": {"default": ""}},
            ]
        },
        {"logging": [{"level": {"default": "WARNING"}}]},
    ],
}

conf = TheConf(metaconf)
