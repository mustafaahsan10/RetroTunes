from app import create_app, db
from app.models import User, Item  # Correct placement, assuming these are defined
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Item': Item}

# Run the application only if the file is executed as the main module
if __name__ == '__main__':
    app.run(debug=True)  # Consider setting debug via an environment variable or direct setting in `create_app`
