# Module_16_7
#### 28/04/2023,00:51 ####
### for SkillFactory Модуль D16.7 ###
### Приложение, создающее сайт "Портал объявлений MMORPG" ###

### В html пункты меню 'Create Post', 'My Posts', 'My Comments' и 'Responses To Me' должны появиться только после регистрации/авторизации пользователя ###
#### Responses To Me - Страница с откликами на объявления текущего пользователя. Возле каждого комментария есть кнопки "Confirm" и "Delete", чтобы принять или удалить отклик. Если пользователь не авторизован, эти кнопки отсутствуют. ####
#### Пока отклик не принят, он не виден никому, кроме того пользователя, к чьему объявлению написан отклик (комментарий). ####
#### На главной странице показывается только 10 последних объявлений со всех категорий. ####
#### Меню слева фильтрует объявления по категориям. ####
#### Раздел bbs/all показывает все объявления со всех категорий постранично в порядке убывания даты создания (свежие - первые). ####
#### Раздел bbs/search позволяет производить поиск по объявлениям по дате, по автору, с поиском по определенному слову в заголовке. ####
#### Каждый пост можно открыть в отдельно странице, там же будут видны все принятые комментарии к нему. ####
#### Посты (объявления) можно редактировать или удалить, пользователь может это делать только со своими объявлениями. #### 
#### Добавлены разделы 'My Posts' и 'My Comments' (их не было в ТЗ): ####
#### 'My Posts' - в нем все объявления текущего пользователя ####
#### 'My Comments' - в нем все комментарии текущего пользователя. Возле каждого комментария есть кнопки "Edit" и "Delete", чтобы чтобы отредактировать или удалить отклик. Если пользователь не авторизован, эти кнопки отсутствуют. ####

##### Для запуска приложения понадобится Терминал #####
Активируем виртуальное окружение в папке ~/django-mmorpg  
активируем его командой **source venv/bin/activate**  
Должен появиться промт с **(venv)** в начале строки.   
Запускать наше приложение нужно в папке billboard, переходим в нее \
командой **cd billboard**  
Далее вводим команду **python3 manage.py runserver**   
Сайт смотрим по адресу ht<span>tp://</span>127.0.0.1:8000/ 
