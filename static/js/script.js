document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('runBtn');
    const pdfUrlInput = document.getElementById('pdfUrl');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorMsg = document.getElementById('errorMsg');
    const spinner = runBtn.querySelector('.spinner');
    const btnText = runBtn.querySelector('.btn-text');

    // Output elements
    const repoLink = document.getElementById('repoLink');
    const pipelineStatus = document.getElementById('pipelineStatus');
    const scanSummary = document.getElementById('scanSummary');
    const demoCode = document.getElementById('demoCode');
    const copyBtn = document.getElementById('copyBtn');

    runBtn.addEventListener('click', async () => {
        const url = pdfUrlInput.value.trim();
        if (!url) return;

        // Reset UI
        errorMsg.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        setLoading(true);

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (data.status === 'failed' || data.error) {
                throw new Error(data.errors ? data.errors.join(', ') : (data.message || 'Unknown error'));
            }

            // Success - Populate Data
            displayResults(data);

        } catch (err) {
            errorMsg.textContent = `Error: ${err.message}`;
            errorMsg.classList.remove('hidden');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        runBtn.disabled = isLoading;
        if (isLoading) {
            spinner.classList.remove('hidden');
            btnText.textContent = 'Analyzing...';
        } else {
            spinner.classList.add('hidden');
            btnText.textContent = 'Start Analysis';
        }
    }

    function displayResults(data) {
        // 1. Repo Link
        repoLink.href = data.best_repo_url || '#';
        repoLink.textContent = data.best_repo_url || 'Not found';

        // 2. Status
        pipelineStatus.textContent = 'Completed';

        // 3. Scan Summary (Pretty Print JSON)
        if (data.scan_report) {
            scanSummary.textContent = JSON.stringify(data.scan_report, null, 2);
        } else {
            scanSummary.textContent = "No scan data available.";
        }

        // 4. Demo Code
        if (data.demo_code) {
            demoCode.textContent = data.demo_code;
        } else {
            demoCode.textContent = "# No demo code generated.";
        }

        // Show container
        resultsContainer.classList.remove('hidden');
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Copy functionality
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(demoCode.textContent).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    });
});
