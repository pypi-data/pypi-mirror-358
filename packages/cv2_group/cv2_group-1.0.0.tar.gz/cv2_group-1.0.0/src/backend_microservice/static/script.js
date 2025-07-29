console.log('[MonitoringTab] script.js loaded');
document.addEventListener('DOMContentLoaded', function() {
  console.log('[MonitoringTab] script.js loaded and DOMContentLoaded');

  // --- API base URL detection ---
  let API_BASE_URL;
  const host = window.location.host;

  if (host.includes('194.171.191.227')) {
    API_BASE_URL = 'http://194.171.191.227:3165'; // Portainer backend
  } else if (host.includes('root-frontend.icybay-728baac8.westeurope.azurecontainerapps.io')) {
    API_BASE_URL = 'https://root-backend.icybay-728baac8.westeurope.azurecontainerapps.io'; // ✅ New backend
  } else {
    API_BASE_URL = 'http://localhost:8000'; // Dev only
  }

  console.log("Using API:", API_BASE_URL);

  // --- Tab Navigation (add monitoring tab support) ---
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabPanes = document.querySelectorAll('.tab-pane');

  function attachMonitoringTabListeners() {
    const logsSlider = document.getElementById('logsSlider');
    const logsSliderValue = document.getElementById('logsSliderValue');
    const logsSliderValueGreen = document.getElementById('logsSliderValueGreen');
    const setRoutingButton = document.getElementById('setRoutingButton');
    const routingStatusMsg = document.getElementById('routingStatusMsg');
    const fetchLogsButton = document.getElementById('fetchLogsButton');
    const logsOutput = document.getElementById('logsOutput');
    const deploymentRadioBlue = document.getElementById('deploymentRadioBlue');
    const deploymentRadioGreen = document.getElementById('deploymentRadioGreen');

    console.log('[MonitoringTab] Attaching listeners...');
    if (!logsSlider) console.log('[MonitoringTab] logsSlider not found');
    if (!logsSliderValue) console.log('[MonitoringTab] logsSliderValue not found');
    if (!logsSliderValueGreen) console.log('[MonitoringTab] logsSliderValueGreen not found');
    if (!setRoutingButton) console.log('[MonitoringTab] setRoutingButton not found');
    if (!routingStatusMsg) console.log('[MonitoringTab] routingStatusMsg not found');
    if (!fetchLogsButton) console.log('[MonitoringTab] fetchLogsButton not found');
    if (!logsOutput) console.log('[MonitoringTab] logsOutput not found');
    if (!deploymentRadioBlue) console.log('[MonitoringTab] deploymentRadioBlue not found');
    if (!deploymentRadioGreen) console.log('[MonitoringTab] deploymentRadioGreen not found');

    if (logsSlider && logsSliderValue && logsSliderValueGreen) {
      logsSlider.addEventListener('input', () => {
        console.log('[MonitoringTab] Slider input event fired');
        logsSliderValue.textContent = logsSlider.value;
        logsSliderValueGreen.textContent = 100 - logsSlider.value;
      });
      // Initialize on load
      logsSliderValue.textContent = logsSlider.value;
      logsSliderValueGreen.textContent = 100 - logsSlider.value;
      console.log('[MonitoringTab] Slider listener attached');
    }

    if (setRoutingButton && logsSlider && routingStatusMsg) {
      setRoutingButton.addEventListener('click', async () => {
        console.log('[MonitoringTab] Set Routing button clicked');
        const bluePercent = parseInt(logsSlider.value, 10);
        const greenPercent = 100 - bluePercent;
        routingStatusMsg.textContent = 'Setting routing...';
        routingStatusMsg.className = 'mt-2 text-sm text-gray-300';
        try {
          const response = await fetch(`${API_BASE_URL}/set-routing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ blue_percent: bluePercent, green_percent: greenPercent })
          });
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to set routing');
          }
          routingStatusMsg.textContent = 'Routing updated successfully!';
          routingStatusMsg.className = 'mt-2 text-sm text-green-400';
          console.log('[MonitoringTab] Routing set successfully');
        } catch (error) {
          routingStatusMsg.textContent = 'Error: ' + error.message;
          routingStatusMsg.className = 'mt-2 text-sm text-red-400';
          console.log('[MonitoringTab] Routing set error:', error.message);
        }
      });
      console.log('[MonitoringTab] Set Routing button listener attached');
    }

    if (fetchLogsButton && logsOutput) {
      fetchLogsButton.addEventListener('click', async () => {
        console.log('[MonitoringTab] Fetch Logs button clicked');
        logsOutput.textContent = 'Fetching logs...';
        let deployment = deploymentRadioBlue && deploymentRadioBlue.checked ? 'blue' : 'green';
        let lines = 200; // Default, could add a UI input for this
        try {
          const response = await fetch(`${API_BASE_URL}/get-logs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ deployment_name: deployment, lines })
          });
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to fetch logs');
          }
          const data = await response.json();
          logsOutput.textContent = data.logs || 'No logs returned.';
          console.log('[MonitoringTab] Logs fetched successfully');
        } catch (error) {
          logsOutput.textContent = 'Error: ' + error.message;
          console.log('[MonitoringTab] Fetch logs error:', error.message);
        }
      });
      console.log('[MonitoringTab] Fetch Logs button listener attached');
    }
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      tabPanes.forEach(pane => {
        if (pane.id === `${tab}-pane`) {
          pane.classList.remove('hidden');
          if (tab === 'monitoring') {
            attachMonitoringTabListeners();
          }
        } else {
          pane.classList.add('hidden');
        }
      });
    });
  });

  // Optionally, attach listeners on initial load if Monitoring tab is active
  const initialActiveTab = document.querySelector('.tab-button.active');
  if (initialActiveTab && initialActiveTab.getAttribute('data-tab') === 'monitoring') {
    attachMonitoringTabListeners();
  }

  // --- Model Comparison Logic ---
  const compareForm = document.getElementById('compareDeploymentsForm');
  if (compareForm) {
    compareForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const resultDiv = document.getElementById('compareDeploymentsResult');
      resultDiv.innerHTML = '<span class="text-gray-300">Comparing deployments...</span>';

      const imageInput = document.getElementById('compareImageInput');
      const numRequests = document.getElementById('compareNumRequests').value || 10;
      const minDelay = document.getElementById('compareMinDelay').value || 0.1;
      const maxDelay = document.getElementById('compareMaxDelay').value || 0.5;

      if (!imageInput.files.length) {
        resultDiv.innerHTML = '<span class="text-red-400">Please select an image.</span>';
        return;
      }

      const formData = new FormData();
      formData.append('image', imageInput.files[0]);
      formData.append('num_requests', numRequests);
      formData.append('min_delay', minDelay);
      formData.append('max_delay', maxDelay);

      try {
        const response = await fetch(`${API_BASE_URL}/test/compare-deployments`, {
          method: 'POST',
          body: formData
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Comparison failed');
        }
        const data = await response.json();
        // Debug: log the backend response
        console.log('Compare Deployments backend response:', data);
        // Render results
        resultDiv.innerHTML = renderComparisonResult(data);
      } catch (error) {
        resultDiv.innerHTML = `<span class="text-red-400">Error: ${error.message}</span>`;
      }
    });
  }
});

// Helper to render the comparison result
function renderComparisonResult(data) {
  if (!data) return '<span class="text-red-400">No data returned.</span>';
  const summary = data.summary || {};
  const blue = summary.blue;
  const green = summary.green;
  const maskStats = data.mask_stats || {};
  const rawResults = data.raw_results || {};

  if (!blue && !green) {
    return '<span class="text-red-400">Error: Backend response missing both blue and green summary data.</span>';
  }
  if (!blue) {
    return '<span class="text-red-400">Error: Backend response missing blue deployment summary.</span>';
  }
  if (!green) {
    return '<span class="text-red-400">Error: Backend response missing green deployment summary.</span>';
  }

  // Get mask images from summary (preferred) or raw_results (fallback)
  const blueMaskImg = blue.mask_image_png_base64 ? `<img src="data:image/png;base64,${blue.mask_image_png_base64}" class="w-32 h-32 object-contain border rounded mb-2 compare-mask-image cursor-pointer" alt="Blue Mask"/>` : (rawResults.blue && rawResults.blue.mask_image_png_base64 ? `<img src="data:image/png;base64,${rawResults.blue.mask_image_png_base64}" class="w-32 h-32 object-contain border rounded mb-2 compare-mask-image cursor-pointer" alt="Blue Mask"/>` : '');
  const greenMaskImg = green.mask_image_png_base64 ? `<img src="data:image/png;base64,${green.mask_image_png_base64}" class="w-32 h-32 object-contain border rounded mb-2 compare-mask-image cursor-pointer" alt="Green Mask"/>` : (rawResults.green && rawResults.green.mask_image_png_base64 ? `<img src="data:image/png;base64,${rawResults.green.mask_image_png_base64}" class="w-32 h-32 object-contain border rounded mb-2 compare-mask-image cursor-pointer" alt="Green Mask"/>` : '');

  return `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 class="text-lg font-bold text-blue-400 mb-2">Blue Deployment</h3>
        <ul class="text-gray-300 text-sm mb-2">
          <li>Avg Time: <b>${blue.average_response_time !== undefined ? blue.average_response_time.toFixed(3) + 's' : 'N/A'}</b></li>
          <li>Success Rate: <b>${blue.success_rate !== undefined ? Math.min((blue.success_rate*100), 100).toFixed(1) + '%' : 'N/A'}</b></li>
          <li>Requests: ${blue.total_requests ?? 'N/A'}, Success: ${blue.successful_requests ?? 'N/A'}, Fail: ${blue.failed_requests ?? 'N/A'}</li>
          <li>Unpacking Failures: ${blue.unpacking_failures ?? 'N/A'}</li>
          <li>Max Time: ${blue.max_response_time !== undefined ? blue.max_response_time.toFixed(3) + 's' : 'N/A'}</li>
          <li>Min Time: ${blue.min_response_time !== undefined ? blue.min_response_time.toFixed(3) + 's' : 'N/A'}</li>
        </ul>
        ${blueMaskImg}
        ${maskStats.blue && maskStats.blue.mask_shape ? `<div class="text-xs text-gray-400">Mask shape: ${JSON.stringify(maskStats.blue.mask_shape)}</div>` : ''}
        ${maskStats.blue && maskStats.blue.mask_sum !== undefined ? `<div class="text-xs text-gray-400">Mask sum: ${maskStats.blue.mask_sum}</div>` : ''}
      </div>
      <div>
        <h3 class="text-lg font-bold text-green-400 mb-2">Green Deployment</h3>
        <ul class="text-gray-300 text-sm mb-2">
          <li>Avg Time: <b>${green.average_response_time !== undefined ? green.average_response_time.toFixed(3) + 's' : 'N/A'}</b></li>
          <li>Success Rate: <b>${green.success_rate !== undefined ? Math.min((green.success_rate*100), 100).toFixed(1) + '%' : 'N/A'}</b></li>
          <li>Requests: ${green.total_requests ?? 'N/A'}, Success: ${green.successful_requests ?? 'N/A'}, Fail: ${green.failed_requests ?? 'N/A'}</li>
          <li>Unpacking Failures: ${green.unpacking_failures ?? 'N/A'}</li>
          <li>Max Time: ${green.max_response_time !== undefined ? green.max_response_time.toFixed(3) + 's' : 'N/A'}</li>
          <li>Min Time: ${green.min_response_time !== undefined ? green.min_response_time.toFixed(3) + 's' : 'N/A'}</li>
        </ul>
        ${greenMaskImg}
        ${maskStats.green && maskStats.green.mask_shape ? `<div class="text-xs text-gray-400">Mask shape: ${JSON.stringify(maskStats.green.mask_shape)}</div>` : ''}
        ${maskStats.green && maskStats.green.mask_sum !== undefined ? `<div class="text-xs text-gray-400">Mask sum: ${maskStats.green.mask_sum}</div>` : ''}
      </div>
    </div>
    <div class="mt-4">
      <h4 class="font-semibold text-white mb-2">Raw Results</h4>
      <pre class="bg-gray-900 text-gray-200 rounded p-2 text-xs overflow-x-auto">${JSON.stringify(rawResults, null, 2)}</pre>
    </div>
  `;
}

// Helper to render the analysis results table
function renderAnalysisResultsTable(roiData) {
  const analysisResultsContainer = document.getElementById('analysisResultsContainer');
  const analysisResultsTableBody = document.querySelector('#analysisResultsTable tbody');
  if (!roiData || roiData.length === 0) {
    analysisResultsContainer.classList.add('hidden');
    analysisResultsTableBody.innerHTML = '';
    return;
  }
  analysisResultsContainer.classList.remove('hidden');
  analysisResultsTableBody.innerHTML = roiData.map((roi, idx) => {
    const analysis = roi.analysis || {};
    return `<tr>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-200">ROI ${idx + 1} (${roi.roi_definition?.x}, ${roi.roi_definition?.y}, ${roi.roi_definition?.width}, ${roi.roi_definition?.height})</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-200">${analysis.length !== undefined ? analysis.length.toFixed(2) : 'N/A'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-200">${analysis.tip_coords ? analysis.tip_coords.join(', ') : 'N/A'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-200">${analysis.base_coords ? analysis.base_coords.join(', ') : 'N/A'}</td>
    </tr>`;
  }).join('');
}
