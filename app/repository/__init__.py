from flask import current_app


def get_trade_repo():
    repo_type = current_app.config.get('REPOSITORY', 'sqlite')
    if repo_type == 'memory':
        from app.repository.memory_repo import InMemoryTradeRepository
        return InMemoryTradeRepository()
    from app.repository.sqlite_repo import SQLiteTradeRepository
    return SQLiteTradeRepository()


def get_user_repo():
    repo_type = current_app.config.get('REPOSITORY', 'sqlite')
    if repo_type == 'memory':
        from app.repository.memory_repo import InMemoryUserRepository
        return InMemoryUserRepository()
    from app.repository.sqlite_repo import SQLiteUserRepository
    return SQLiteUserRepository()
