import util

session = util.load_session()
util.update_startup_info(session)
session.close()
