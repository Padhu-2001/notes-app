import os
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import firestore, storage

app = Flask(__name__)

# Use the specific database you created
db = firestore.Client(database="notes-db")
storage_client = storage.Client()
BUCKET_NAME = os.environ.get('BUCKET_NAME')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        filename = f"{title.replace(' ', '_')}.md"

        try:
            # Upload markdown to Storage
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(filename)
            blob.upload_from_string(content, content_type='text/markdown')

            # Save reference to Firestore
            db.collection('notes').add({
                'title': title,
                'file_url': f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}",
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            return redirect(url_for('index'))
        except Exception as e:
            return f"Error: {str(e)}", 500

    # Get list of notes
    notes_query = db.collection('notes').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    return render_template('index.html', notes=notes_query)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
