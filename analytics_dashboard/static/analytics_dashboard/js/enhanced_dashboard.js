// Enhanced Dashboard JavaScript with all advanced features

class EcoGuardDashboard {
    constructor() {
        this.autoRefreshInterval = null;
        this.isAutoRefreshing = false;
        this.currentChartType = 'line';
        this.speechRecognition = null;
        this.currentData = null;
        this.init();
    }

    init() {
        this.loadCharts();
        this.initializeVoiceRecognition();
        this.setupEventListeners();
        this.loadDarkModePreference();
        
        // Remove loading skeletons after data loads
        setTimeout(() => {
            document.querySelectorAll('.loading-skeleton').forEach(skeleton => {
                skeleton.style.display = 'none';
            });
        }, 2000);
    }

    setupEventListeners() {
        // Time filter change
        document.getElementById('timeFilter')?.addEventListener('change', () => this.updateGraphs());
        
        // Chart type change
        document.getElementById('chartType')?.addEventListener('change', () => this.switchChartType());
        
        // Auto refresh toggle
        document.getElementById('autoRefreshBtn')?.addEventListener('click', () => this.toggleAutoRefresh());
        
        // Export buttons
        document.querySelectorAll('[onclick*="exportData"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const format = btn.textContent.includes('CSV') ? 'csv' : 'excel';
                this.exportData(format);
            });
        });
        
        // Chart export buttons
        document.querySelectorAll('[onclick*="exportChart"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const format = btn.textContent.includes('PNG') ? 'png' : 'pdf';
                this.exportChart(format);
            });
        });
    }

    async loadCharts() {
        try {
            const filter = document.getElementById('timeFilter')?.value || 'month';
            const chartType = document.getElementById('chartType')?.value || 'line';
            
            const response = await fetch(`/dashboard/api/data/?filter=${filter}&chart_type=${chartType}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error('Failed to fetch data');
            
            this.currentData = await response.json();
            this.renderCharts();
            this.updateAchievements();
            this.updateAIInsights();
            
        } catch (error) {
            console.error('Error loading charts:', error);
            this.showErrorMessage('Failed to load dashboard data');
        }
    }

    renderCharts() {
        if (!this.currentData) return;

        // Main Chart
        this.renderMainChart();
        
        // Radar Chart
        this.renderRadarChart();
        
        // Category Chart
        this.renderCategoryChart();
        
        // Waterfall Chart
        this.renderWaterfallChart();
    }

    renderMainChart() {
        const { dates, emissions, transport, electricity, food, plastic } = this.currentData;
        
        let trace;
        const isDarkMode = document.body.classList.contains('dark-mode');
        const textColor = isDarkMode ? '#ffffff' : '#333333';
        
        switch (this.currentChartType) {
            case 'line':
                trace = {
                    x: dates,
                    y: emissions,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'CO₂ Emissions',
                    line: { color: '#2ecc71', width: 3 },
                    marker: { size: 8, color: '#2ecc71' },
                    hovertemplate: '<b>%{x}</b><br>CO₂: %{y:.1f} kg<extra></extra>'
                };
                break;
                
            case 'bar':
                trace = {
                    x: dates.slice(-7),
                    y: emissions.slice(-7),
                    type: 'bar',
                    name: 'CO₂ Emissions',
                    marker: { color: '#3498db' },
                    hovertemplate: '<b>%{x}</b><br>CO₂: %{y:.1f} kg<extra></extra>'
                };
                break;
                
            case 'pie':
                trace = {
                    labels: this.currentData.categories,
                    values: this.currentData.category_totals,
                    type: 'pie',
                    marker: { colors: ['#e74c3c', '#f39c12', '#2ecc71', '#3498db'] },
                    hovertemplate: '<b>%{label}</b><br>%{value:.1f} kg (%{percent})<extra></extra>'
                };
                break;
                
            case 'heatmap':
                // Create weekly heatmap data
                const weeks = Math.ceil(dates.length / 7);
                const heatmapData = [];
                const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                
                for (let week = 0; week < weeks; week++) {
                    const weekData = [];
                    for (let day = 0; day < 7; day++) {
                        const index = week * 7 + day;
                        weekData.push(index < emissions.length ? emissions[index] : 0);
                    }
                    heatmapData.push(weekData);
                }
                
                trace = {
                    z: heatmapData,
                    x: days,
                    y: Array.from({length: weeks}, (_, i) => `Week ${i + 1}`),
                    type: 'heatmap',
                    colorscale: 'RdYlGn_r',
                    hovertemplate: '<b>%{y} - %{x}</b><br>CO₂: %{z:.1f} kg<extra></extra>'
                };
                break;
        }

        const layout = {
            title: {
                text: 'CO₂ Emissions Analysis',
                font: { color: textColor, size: 18 }
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: textColor },
            xaxis: { 
                gridcolor: isDarkMode ? '#444' : '#ddd',
                title: this.currentChartType === 'heatmap' ? 'Day of Week' : 'Date'
            },
            yaxis: { 
                gridcolor: isDarkMode ? '#444' : '#ddd',
                title: this.currentChartType === 'heatmap' ? 'Week' : 'CO₂ (kg)'
            },
            margin: { t: 50, r: 30, b: 50, l: 50 }
        };

        Plotly.newPlot('mainChart', [trace], layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToAdd: [{
                name: 'Drill Down',
                icon: Plotly.Icons.zoom_plus,
                click: () => this.drillDown('emissions')
            }]
        });
    }

    renderRadarChart() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const textColor = isDarkMode ? '#ffffff' : '#333333';
        
        const userTrace = {
            type: 'scatterpolar',
            r: this.currentData.radar_user,
            theta: this.currentData.categories,
            fill: 'toself',
            name: 'Your Performance',
            marker: { color: '#2ecc71' },
            line: { color: '#2ecc71' }
        };
        
        const globalTrace = {
            type: 'scatterpolar',
            r: this.currentData.radar_global,
            theta: this.currentData.categories,
            fill: 'toself',
            name: 'Global Average',
            marker: { color: '#e74c3c' },
            line: { color: '#e74c3c' }
        };

        const layout = {
            title: {
                text: 'Performance vs Global Average',
                font: { color: textColor, size: 16 }
            },
            polar: {
                radialaxis: { 
                    visible: true, 
                    range: [0, 10],
                    gridcolor: isDarkMode ? '#444' : '#ddd',
                    tickfont: { color: textColor }
                },
                angularaxis: {
                    tickfont: { color: textColor }
                }
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: textColor },
            margin: { t: 50, r: 30, b: 30, l: 30 }
        };

        Plotly.newPlot('radarChart', [userTrace, globalTrace], layout, { responsive: true });
    }

    renderCategoryChart() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const textColor = isDarkMode ? '#ffffff' : '#333333';
        
        const trace = {
            x: this.currentData.categories,
            y: this.currentData.category_totals,
            type: 'bar',
            marker: { 
                color: ['#e74c3c', '#f39c12', '#2ecc71', '#3498db'],
                line: { color: isDarkMode ? '#666' : '#fff', width: 2 }
            },
            hovertemplate: '<b>%{x}</b><br>Total: %{y:.1f} kg<extra></extra>'
        };

        const layout = {
            title: {
                text: 'Emissions by Category',
                font: { color: textColor, size: 16 }
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: textColor },
            xaxis: { 
                gridcolor: isDarkMode ? '#444' : '#ddd',
                title: 'Category'
            },
            yaxis: { 
                gridcolor: isDarkMode ? '#444' : '#ddd',
                title: 'CO₂ (kg)'
            },
            margin: { t: 50, r: 30, b: 50, l: 50 }
        };

        Plotly.newPlot('categoryChart', [trace], layout, { responsive: true });
    }

    renderWaterfallChart() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const textColor = isDarkMode ? '#ffffff' : '#333333';
        
        // Generate sample waterfall data
        const changes = [20, -5, 10, -8, 15, -3];
        const weeks = changes.map((_, i) => `Week ${i + 1}`);
        
        const trace = {
            type: 'waterfall',
            x: weeks,
            y: changes,
            connector: { line: { color: isDarkMode ? '#666' : 'rgb(63, 63, 63)' } },
            increasing: { marker: { color: '#e74c3c' } },
            decreasing: { marker: { color: '#2ecc71' } },
            hovertemplate: '<b>%{x}</b><br>Change: %{y:+.1f} kg<extra></extra>'
        };

        const layout = {
            title: {
                text: 'Weekly CO₂ Changes',
                font: { color: textColor, size: 16 }
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: textColor },
            xaxis: { 
                gridcolor: isDarkMode ? '#444' : '#ddd',
                title: 'Week'
            },
            yaxis: { 
                gridcolor: isDarkMode ? '#444' : '#ddd',
                title: 'Change (kg)'
            },
            margin: { t: 50, r: 30, b: 50, l: 50 }
        };

        Plotly.newPlot('waterfallChart', [trace], layout, { responsive: true });
    }

    updateAchievements() {
        if (!this.currentData.achievements) return;
        
        const achievementsGrid = document.querySelector('.achievements-grid');
        if (!achievementsGrid) return;
        
        achievementsGrid.innerHTML = this.currentData.achievements.map(achievement => `
            <div class="achievement-badge ${achievement.unlocked ? 'unlocked' : 'locked'}" 
                 onclick="dashboard.shareAchievement('${achievement.title}')">
                <div class="badge-icon">${achievement.icon}</div>
                <div class="badge-title">${achievement.title}</div>
                <div class="badge-description">${achievement.description}</div>
                ${achievement.unlocked ? '<div class="badge-status">✅ Unlocked</div>' : '<div class="badge-status">🔒 Locked</div>'}
            </div>
        `).join('');
    }

    updateAIInsights() {
        if (!this.currentData.ai_insights) return;
        
        const insightsGrid = document.querySelector('.insights-grid');
        if (!insightsGrid) return;
        
        insightsGrid.innerHTML = this.currentData.ai_insights.map(insight => `
            <div class="insight-card">
                <div class="insight-icon">${insight.icon}</div>
                <div class="insight-title">${insight.title}</div>
                <div class="insight-text">${insight.text}</div>
            </div>
        `).join('');
    }

    // Dark mode functionality
    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const icon = document.getElementById('darkModeIcon');
        if (document.body.classList.contains('dark-mode')) {
            icon.className = 'fas fa-sun';
            localStorage.setItem('darkMode', 'enabled');
        } else {
            icon.className = 'fas fa-moon';
            localStorage.setItem('darkMode', 'disabled');
        }
        
        // Re-render charts with new theme
        this.renderCharts();
    }

    loadDarkModePreference() {
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
            const icon = document.getElementById('darkModeIcon');
            if (icon) icon.className = 'fas fa-sun';
        }
    }

    // Auto refresh functionality
    toggleAutoRefresh() {
        const btn = document.getElementById('autoRefreshBtn');
        if (!btn) return;
        
        if (this.isAutoRefreshing) {
            clearInterval(this.autoRefreshInterval);
            btn.innerHTML = '<i class="fas fa-play"></i> Start';
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary');
            this.isAutoRefreshing = false;
        } else {
            this.autoRefreshInterval = setInterval(() => this.updateGraphs(), 30000);
            btn.innerHTML = '<i class="fas fa-pause"></i> Stop';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
            this.isAutoRefreshing = true;
        }
    }

    async updateGraphs() {
        document.querySelectorAll('.dashboard-card').forEach(card => {
            card.style.opacity = '0.7';
        });
        
        await this.loadCharts();
        
        document.querySelectorAll('.dashboard-card').forEach(card => {
            card.style.opacity = '1';
        });
    }

    switchChartType() {
        this.currentChartType = document.getElementById('chartType')?.value || 'line';
        this.renderMainChart();
    }

    // Export functionality
    exportData(format) {
        if (!this.currentData) return;
        
        let content, filename, mimeType;
        
        if (format === 'csv') {
            const headers = ['Date', 'CO2_Emissions', 'Transport', 'Electricity', 'Food', 'Plastic'];
            const rows = this.currentData.dates.map((date, i) => [
                date,
                this.currentData.emissions[i],
                this.currentData.transport[i],
                this.currentData.electricity[i],
                this.currentData.food[i],
                this.currentData.plastic[i]
            ]);
            
            content = [headers, ...rows].map(row => row.join(',')).join('\n');
            filename = 'ecoguard_data.csv';
            mimeType = 'text/csv';
        }
        
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    exportChart(format) {
        const chartElement = document.getElementById('mainChart');
        if (!chartElement) return;
        
        if (format === 'png') {
            html2canvas(chartElement).then(canvas => {
                const link = document.createElement('a');
                link.download = 'ecoguard_chart.png';
                link.href = canvas.toDataURL();
                link.click();
            });
        } else if (format === 'pdf') {
            html2canvas(chartElement).then(canvas => {
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF();
                const imgData = canvas.toDataURL('image/png');
                pdf.addImage(imgData, 'PNG', 10, 10, 190, 100);
                pdf.save('ecoguard_chart.pdf');
            });
        }
    }

    // Drill down functionality
    drillDown(chartType) {
        const modal = document.createElement('div');
        modal.className = 'drill-down-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Detailed ${chartType} Analysis</h3>
                    <button class="modal-close" onclick="this.closest('.drill-down-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div id="drillDownChart" style="height: 400px;"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Render detailed chart
        setTimeout(() => {
            this.renderDetailedChart('drillDownChart', chartType);
        }, 100);
    }

    renderDetailedChart(containerId, chartType) {
        // Render a more detailed version of the selected chart
        const trace = {
            x: this.currentData.dates,
            y: this.currentData.emissions,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Detailed CO₂ Emissions',
            line: { color: '#2ecc71', width: 2 },
            marker: { size: 6 }
        };

        const layout = {
            title: 'Detailed Emissions Analysis',
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            margin: { t: 50, r: 30, b: 50, l: 50 }
        };

        Plotly.newPlot(containerId, [trace], layout, { responsive: true });
    }

    // Voice recognition
    initializeVoiceRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.speechRecognition = new webkitSpeechRecognition();
            this.speechRecognition.continuous = false;
            this.speechRecognition.interimResults = false;
            this.speechRecognition.lang = 'en-US';

            this.speechRecognition.onresult = (event) => {
                const command = event.results[0][0].transcript.toLowerCase();
                this.processVoiceCommand(command);
            };

            this.speechRecognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showErrorMessage('Voice recognition failed');
            };
        }
    }

    startVoiceCommand() {
        if (!this.speechRecognition) {
            this.showErrorMessage('Voice recognition not supported in this browser');
            return;
        }
        
        const btn = document.querySelector('.voice-btn');
        btn.classList.add('listening');
        this.speechRecognition.start();
        
        setTimeout(() => {
            btn.classList.remove('listening');
        }, 5000);
    }

    processVoiceCommand(command) {
        console.log('Voice command:', command);
        
        if (command.includes('show') && command.includes('month')) {
            document.getElementById('timeFilter').value = 'month';
            this.updateGraphs();
            this.showSuccessMessage('Showing monthly data');
        } else if (command.includes('show') && command.includes('week')) {
            document.getElementById('timeFilter').value = 'week';
            this.updateGraphs();
            this.showSuccessMessage('Showing weekly data');
        } else if (command.includes('dark mode')) {
            this.toggleDarkMode();
            this.showSuccessMessage('Dark mode toggled');
        } else if (command.includes('export')) {
            this.exportData('csv');
            this.showSuccessMessage('Data exported');
        } else if (command.includes('refresh')) {
            this.updateGraphs();
            this.showSuccessMessage('Dashboard refreshed');
        } else {
            this.showErrorMessage(`Command "${command}" not recognized. Try "show last month", "dark mode", or "export data"`);
        }
    }

    // Social sharing
    shareAchievement(title) {
        const text = `I just unlocked "${title}" on EcoGuard! 🌱 Join me in reducing carbon emissions!`;
        
        if (navigator.share) {
            navigator.share({
                title: 'EcoGuard Achievement',
                text: text,
                url: window.location.href
            }).catch(console.error);
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(text + ' ' + window.location.href);
            this.showSuccessMessage('Achievement copied to clipboard!');
        } else {
            this.showErrorMessage('Sharing not supported - Copy link manually');
        }
    }

    // Utility methods
    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }

    showErrorMessage(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '600',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });
        
        if (type === 'success') {
            toast.style.background = '#2ecc71';
        } else if (type === 'error') {
            toast.style.background = '#e74c3c';
        } else {
            toast.style.background = '#3498db';
        }
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize dashboard
const dashboard = new EcoGuardDashboard();

// Global functions for backward compatibility
function toggleDarkMode() { dashboard.toggleDarkMode(); }
function updateGraphs() { dashboard.updateGraphs(); }
function switchChartType() { dashboard.switchChartType(); }
function toggleAutoRefresh() { dashboard.toggleAutoRefresh(); }
function exportData(format) { dashboard.exportData(format); }
function exportChart(format) { dashboard.exportChart(format); }
function drillDown(type) { dashboard.drillDown(type); }
function startVoiceCommand() { dashboard.startVoiceCommand(); }
function switchView(type) { dashboard.switchView(type); }
function analyzeChanges() { dashboard.analyzeChanges(); }