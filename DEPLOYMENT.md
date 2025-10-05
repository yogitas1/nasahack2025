# Deployment Checklist

## Pre-Deployment Verification

### 1. Required Files Check
- [ ] `app.py` - Main Streamlit application
- [ ] `rag_search.py` - RAG search module
- [ ] `requirements.txt` - All dependencies listed
- [ ] `.streamlit/config.toml` - Streamlit configuration
- [ ] `data/embeddings.pkl` - Embeddings file exists
- [ ] `data/knowledge_base.json` - Knowledge base exists
- [ ] `data/image_knowledge_base.json` - Image metadata exists
- [ ] `images/` folder - Contains PNG/JPG files (no PDFs)
- [ ] `README.md` - Documentation updated

### 2. Code Quality
- [ ] No debug `print()` statements in production code
- [ ] All imports are used and necessary
- [ ] Error handling in place for image loading
- [ ] Graceful fallbacks for API failures

### 3. Environment Variables
- [ ] `.env` file is in `.gitignore` (not committed)
- [ ] OpenAI API key is set locally for testing
- [ ] Ready to add API key as Streamlit Cloud secret

### 4. Dependencies
Current `requirements.txt` includes:
```
PyPDF2>=3.0.1
openai>=1.0.0
python-dotenv>=1.0.0
numpy>=1.24.0
streamlit>=1.28.0
requests>=2.28.0
pillow>=10.0.0
```

### 5. Image Files
- [ ] All images in `images/` folder are PNG or JPG format
- [ ] No PDF files referenced in `image_knowledge_base.json`
- [ ] Image paths in JSON match actual filenames exactly
- [ ] All images are under GitHub file size limits (100MB per file)

## Deployment Steps (Streamlit Cloud)

### Step 1: Prepare Repository
```bash
# Verify all required files are committed
git status

# Add any missing files
git add data/ images/ .streamlit/
git commit -m "Prepare for deployment"
git push
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `app.py`
6. Click "Advanced settings"
7. Add secrets:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
8. Click "Deploy"

### Step 3: Post-Deployment Testing
- [ ] App loads without errors
- [ ] Chat functionality works
- [ ] Images display correctly
- [ ] Source citations appear
- [ ] WorldPop integration works (if applicable)
- [ ] Error messages are user-friendly

## Troubleshooting

### Images Not Displaying
- Check that image filenames in `data/image_knowledge_base.json` match exactly
- Verify all images are PNG or JPG (not PDF)
- Check file paths are relative: `images/filename.png`

### Missing Dependencies
- Verify `requirements.txt` is complete
- Check Python version compatibility (3.8+)

### API Errors
- Verify OpenAI API key is set in Streamlit secrets
- Check API key has sufficient credits
- Verify key has access to required models (gpt-4o-mini, text-embedding-3-small)

### Large File Size
- Compress images if needed
- Use Git LFS for files over 100MB
- Consider hosting large files externally

## Performance Optimization

- [ ] Embeddings are pre-computed (not generated on each query)
- [ ] Knowledge base loaded once at startup using session state
- [ ] Image loading has error handling to prevent crashes
- [ ] API calls have appropriate timeouts

## Security

- [ ] `.env` file not committed to repository
- [ ] API keys stored in Streamlit secrets
- [ ] No sensitive data in code or comments
- [ ] CORS and XSRF protection enabled in config

## Monitoring

After deployment, monitor:
- Response times
- Error rates
- API usage and costs
- User feedback

## Rollback Plan

If deployment fails:
1. Check Streamlit Cloud logs
2. Test locally with: `streamlit run app.py`
3. Revert to last working commit if needed
4. Contact support if infrastructure issue

## Notes

- First deployment may take 5-10 minutes
- App will restart when you push new commits
- Streamlit Cloud has resource limits (CPU, RAM)
- Free tier has usage limits - monitor carefully
