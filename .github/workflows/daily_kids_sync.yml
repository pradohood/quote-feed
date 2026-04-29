name: Daily E-Ink Update
on:
  schedule:
    - cron: '0 12 * * *'
  workflow_dispatch:
jobs:
  update_images:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Dependencies
        run: pip install Pillow groq requests
      
      - name: Generate Daily Content
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          python generate_daily.py
          if [ $? -eq 0 ]; then
            echo "✓ generate_daily.py completed successfully"
          else
            echo "✗ generate_daily.py failed with exit code $?"
            exit 1
          fi
      
      - name: Fetch Asher Comic
        run: |
          python fetch_asher.py
          if [ $? -eq 0 ]; then
            echo "✓ fetch_asher.py completed successfully"
          else
            echo "✗ fetch_asher.py failed with exit code $?"
            exit 1
          fi
      
      - name: Verify All Files Created
        run: |
          echo "=== Checking generated files ==="
          for file in history.png animal.png affirmation.png joke.png asher_comic.png; do
            if [ -f "$file" ]; then
              size=$(ls -lh "$file" | awk '{print $5}')
              echo "✓ $file ($size)"
            else
              echo "✗ $file MISSING"
            fi
          done
          
          if ! [ -f asher_comic.png ]; then
            echo ""
            echo "ERROR: asher_comic.png was not created!"
            exit 1
          fi
      
      - name: Install rclone
        run: curl https://rclone.org/install.sh | sudo bash
      
      - name: Upload to Dropbox
        env:
          RCLONE_CONFIG_DROPBOX_TYPE: dropbox
          RCLONE_CONFIG_DROPBOX_TOKEN: ${{ secrets.RCLONE_DROPBOX_TOKEN }}
        run: |
          echo "=== Uploading files to Dropbox ==="
          rclone copy ./history.png dropbox:"Apps/pradohood github/"
          rclone copy ./animal.png dropbox:"Apps/pradohood github/"
          rclone copy ./affirmation.png dropbox:"Apps/pradohood github/"
          rclone copy ./joke.png dropbox:"Apps/pradohood github/"
          rclone copy ./asher_comic.png dropbox:"Apps/pradohood github/"
          
          if [ $? -eq 0 ]; then
            echo "✓ All files uploaded successfully"
          else
            echo "✗ rclone upload failed"
            exit 1
          fi
