# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 1536  # Находится в системе / активно
COMPLETED = 1435  # Завершено / обработано

# Статусы обработчика
FREE = 0  # Свободно
PROCESSING = 1  # В обработке / занято
BROKEN = 2  # В обработке / занято

# Типы событий
APPLICATION_EVENT = 'a'
HANDLER_EVENT = 'h'
HANDLER_COMPLETED_EVENT = 'C'
HANDLER_BROKEN_EVENT = 'B'
HANDLER_RECOVER_EVENT = 'R'
