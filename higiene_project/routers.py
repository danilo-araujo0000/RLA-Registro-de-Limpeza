class OracleRouter:
    def db_for_read(self, model, **hints):
        # Modelos de controle que usam o banco SQLite (default)
        if model.__name__ in {'IPPermitido', 'DispositivoPermitido'}:
            return 'default'
        if model._meta.app_label == 'registro':
            return 'oracle'
        return None

    def db_for_write(self, model, **hints):
        # Modelos de controle que usam o banco SQLite (default)
        if model.__name__ in {'IPPermitido', 'DispositivoPermitido'}:
            return 'default'
        if model._meta.app_label == 'registro':
            return 'oracle'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'registro' or \
           obj2._meta.app_label == 'registro':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Modelos de controle migram apenas no SQLite
        if model_name in {'ippermitido', 'dispositivopermitido'}:
            return db == 'default'
        if app_label == 'registro':
            return db == 'oracle'
        return None
