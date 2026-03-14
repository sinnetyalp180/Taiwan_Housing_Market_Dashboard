'''
dash
dash-bootstrap-components
dash-leaflet

'''


from dashboard.content import app
import os
from dotenv import load_dotenv
load_dotenv()




if __name__ == '__main__':
    app.run(
        debug = os.getenv('DEBUG')=='True', 
        dev_tools_hot_reload=True,             # 提高靈敏，可以手動啟用 Hot Reload (Ctrl + S)
        port = os.getenv('PORT'),
    ) 