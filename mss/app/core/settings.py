from dataclasses import dataclass


@dataclass
class AppearanceSettings:
    window_background: str
    title_background: str
    button_background: str
    nav_button_background: str
    text: str


@dataclass
class ProgramSettings:
    selected_config: str
    last_update_check: str
    version: str
    notes: str
    check_updates_on_startup: bool


@dataclass
class JsonMetadataSettings:
    version: str
    date: str
    comment: str


@dataclass
class DatabaseUpdateSettings:
    br: str
    pt: str
    mx: str
    md: str


@dataclass
class ConnectionSettings:
    name: str
    server: str
    username: str
    password: str


@dataclass
class RedisInstanceSettings:
    name: str
    ip: str
    port: int


@dataclass
class RedisGroupSettings:
    name: str
    instances: list[RedisInstanceSettings]


@dataclass
class Settings:
    program: ProgramSettings
    appearance: AppearanceSettings
    json_metadata: JsonMetadataSettings
    database_updates: DatabaseUpdateSettings
    wall_databases: list[str]
    connections: list[ConnectionSettings]
    redis_groups: list[RedisGroupSettings]
