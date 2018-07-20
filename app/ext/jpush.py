from jpush import JPush as _JPush


class JPush(_JPush):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        config = app.config.copy()
        app_key = config.get('JPUSH_APP_KEY', None)
        master_secret = config.get('JPUSH_MASTER_SECRET', None)
        if app_key or master_secret:
            return super().__init__(app_key, master_secret)


Jpush = JPush()
