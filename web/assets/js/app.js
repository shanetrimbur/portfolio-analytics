// web/assets/js/app.js

// Sample data generation (simulating backend)
function generateSampleData() {
    const assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'BRK.A'];
    const returns = assets.map(() => Math.random() * 0.2 + 0.05);
    const weights = assets.map(() => Math.random());
    const sum = weights.reduce((a, b) => a + b, 0);
    const normalizedWeights = weights.map(w => w / sum);
    
    return {
        assets,
        weights: normalizedWeights,
        returns,
        metrics: {
            'Expected Return': (Math.random() * 0.15 + 0.05).toFixed(4),
            'Volatility': (Math.random() * 0.12 + 0.08).toFixed(4),
            'Sharpe Ratio': (Math.random() * 1.5 + 0.5).toFixed(4),
            'Max Drawdown': (-Math.random() * 0.2).toFixed(4)
        }
    };
}

// Plot efficient frontier
function plotEfficientFrontier() {
    const points = Array.from({length: 50}, (_, i) => ({
        return: Math.random() * 0.2 + 0.05,
        risk: Math.random() * 0.15 + 0.05
    })).sort((a, b) => a.risk - b.risk);

    const trace = {
        x: points.map(p => p.risk),
        y: points.map(p => p.return),
        mode: 'lines+markers',
        type: 'scatter',
        name: 'Portfolio',
        line: {
            color: '#3b82f6',
            width: 2
        },
        marker: {
            size: 6,
            color: '#3b82f6'
        }
    };

    const layout = {
        title: 'Efficient Frontier',
        xaxis: { 
            title: 'Risk (Volatility)',
            gridcolor: '#f0f0f0'
        },
        yaxis: { 
            title: 'Expected Return',
            gridcolor: '#f0f0f0'
        },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        margin: { t: 40, r: 20, b: 40, l: 40 }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('efficient-frontier', [trace], layout, config);
}

// Plot portfolio weights
function plotWeights(data) {
    const trace = {
        x: data.assets,
        y: data.weights,
        type: 'bar',
        marker: {
            color: '#3b82f6'
        }
    };

    const layout = {
        title: 'Portfolio Weights',
        yaxis: { 
            title: 'Weight',
            gridcolor: '#f0f0f0'
        },
        xaxis: {
            gridcolor: '#f0f0f0'
        },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        margin: { t: 40, r: 20, b: 40, l: 40 }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('weights-chart', [trace], layout, config);
}

// Update metrics display
function updateMetrics(metrics) {
    const metricsDisplay = document.getElementById('metrics-display');
    metricsDisplay.innerHTML = Object.entries(metrics)
        .map(([key, value]) => `
            <div class="metrics-card bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">${key}</div>
                <div class="text-lg font-semibold text-blue-600">${value}</div>
            </div>
        `).join('');
}

// Event handlers
function handleOptimize() {
    const riskFreeRate = parseFloat(document.getElementById('risk-free-rate').value);
    const optimizationTarget = document.getElementById('optimization-target').value;
    
    // Add loading state
    document.getElementById('optimize-btn').classList.add('opacity-75', 'cursor-wait');
    
    // Simulate API call delay
    setTimeout(() => {
        const data = generateSampleData();
        plotEfficientFrontier();
        plotWeights(data);
        updateMetrics(data.metrics);
        
        // Remove loading state
        document.getElementById('optimize-btn').classList.remove('opacity-75', 'cursor-wait');
    }, 500);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const data = generateSampleData();
    plotEfficientFrontier();
    plotWeights(data);
    updateMetrics(data.metrics);
    
    // Add event listeners
    document.getElementById('optimize-btn').addEventListener('click', handleOptimize);
    window.addEventListener('resize', () => {
        plotEfficientFrontier();
        plotWeights(generateSampleData());
    });
});
