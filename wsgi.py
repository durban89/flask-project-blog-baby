# _*_ coding: utf-8 _*_
from baby import (
    socketio, application,
    # make_app_with_prefix,
    # make_app_with_subdomain
)

# from baby.dispatcher import (
#     PathDispatcher,
#     SubdomainDispatcher
# )

if __name__ == '__main__':
    # subdomain转发到other application
    # application.wsgi_app = SubdomainDispatcher(
    #     'baby.local',
    #     make_app_with_subdomain
    # )

    # path 转发到other application
    # application.wsgi_app = PathDispatcher(
    #     application.wsgi_app,
    #     make_app_with_prefix
    # )

    socketio.run(application, debug=True)
