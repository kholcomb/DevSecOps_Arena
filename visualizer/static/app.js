/**
 * K8sQuest Cluster Visualizer
 * Enhanced with modern interactions, SVG icons, and animations
 */

// ============================================
// SVG Icon Library
// ============================================
const K8S_ICONS = {
    pod: {
        path: 'M12,2L2,7v10l10,5l10,-5V7L12,2zM12,4.3l7.5,3.75v7.5L12,19.3l-7.5,-3.75v-7.5L12,4.3z M8,10v8l4,2l4,-2v-8l-4,-2L8,10z',
        viewBox: '0 0 24 24'
    },
    deployment: {
        path: 'M3,3h18v18H3V3z M5,5v14h14V5H5z M7,7h10v10H7V7z M9,9v6h6V9H9z M11,11h2v2h-2V11z',
        viewBox: '0 0 24 24'
    },
    service: {
        path: 'M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10,-4.48,10,-10S17.52,2,12,2z M12,20c-4.41,0,-8,-3.59,-8,-8s3.59,-8,8,-8s8,3.59,8,8 S16.41,20,12,20z M8,11h8v2H8V11z M11,8h2v8h-2V8z',
        viewBox: '0 0 24 24'
    },
    ingress: {
        path: 'M12,2L2,12h3v8h6v-6h2v6h6v-8h3L12,2z M12,5.7L17,10.7v7.3h-2v-6H9v6H7v-7.3L12,5.7z',
        viewBox: '0 0 24 24'
    },
    configmap: {
        path: 'M19,3H5C3.9,3,3,3.9,3,5v14c0,1.1,0.9,2,2,2h14c1.1,0,2,-0.9,2,-2V5C21,3.9,20.1,3,19,3z M19,19H5V5h14V19z M7,10h10v2H7V10z M7,14h7v2H7V14z M7,7h10v1H7V7z',
        viewBox: '0 0 24 24'
    },
    secret: {
        path: 'M12,1L3,5v6c0,5.55,3.84,10.74,9,12c5.16,-1.26,9,-6.45,9,-12V5L12,1z M12,11.99h5c-0.47,2.76,-2.14,5.19,-5,6.41V11.99z M12,10V3.19l7,3.11V10H12z',
        viewBox: '0 0 24 24'
    },
    networkpolicy: {
        path: 'M12,8c-2.21,0,-4,1.79,-4,4s1.79,4,4,4s4,-1.79,4,-4S14.21,8,12,8z M2,12c0,1.83,0.49,3.54,1.35,5.02L5,15.37C4.38,14.37,4,13.23,4,12 c0,-4.41,3.59,-8,8,-8c1.23,0,2.37,0.38,3.37,1L13.72,6.65C12.54,5.49,11.33,5,10,5C6.69,5,4,7.69,4,11z M12,20c-1.23,0,-2.37,-0.38,-3.37,-1l1.65,-1.65 C11.46,18.51,12.67,19,14,19c3.31,0,6,-2.69,6,-6c0,-1.33,-0.49,-2.54,-1.35,-3.46l1.65,-1.65C21.12,8.46,22,10.17,22,12 C22,17.52,17.52,22,12,22z',
        viewBox: '0 0 24 24'
    },
    statefulset: {
        path: 'M19,3H5C3.9,3,3,3.9,3,5v14c0,1.1,0.9,2,2,2h14c1.1,0,2,-0.9,2,-2V5C21,3.9,20.1,3,19,3z M7,19c-1.1,0,-2,-0.9,-2,-2s0.9,-2,2,-2 s2,0.9,2,2S8.1,19,7,19z M7,13c-1.1,0,-2,-0.9,-2,-2s0.9,-2,2,-2s2,0.9,2,2S8.1,13,7,13z M7,7C5.9,7,5,6.1,5,5s0.9,-2,2,-2 s2,0.9,2,2S8.1,7,7,7z M19,19h-8v-2h8V19z M19,13h-8v-2h8V13z M19,7h-8V5h8V7z',
        viewBox: '0 0 24 24'
    },
    pvc: {
        path: 'M4,4h16c1.1,0,2,0.9,2,2v12c0,1.1,-0.9,2,-2,2H4c-1.1,0,-2,-0.9,-2,-2V6C2,4.9,2.9,4,4,4z M4,18h16V8H4V18z M6,10h12v2H6V10z M6,14h8v2H6V14z',
        viewBox: '0 0 24 24'
    },
    replicaset: {
        path: 'M4,6H2v14c0,1.1,0.9,2,2,2h14v-2H4V6z M20,2H8C6.9,2,6,2.9,6,4v12c0,1.1,0.9,2,2,2h12c1.1,0,2,-0.9,2,-2V4 C22,2.9,21.1,2,20,2z M20,16H8V4h12V16z M14,6h-4v4H6v4h4v4h4v-4h4v-4h-4V6z',
        viewBox: '0 0 24 24'
    },
    hpa: {
        path: 'M3,13h2v-2H3V13z M3,17h2v-2H3V17z M3,9h2V7H3V9z M7,13h14v-2H7V13z M7,17h14v-2H7V17z M7,7v2h14V7H7z',
        viewBox: '0 0 24 24'
    },
    role: {
        path: 'M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10,-4.48,10,-10S17.52,2,12,2z M12,5c1.66,0,3,1.34,3,3s-1.34,3,-3,3s-3,-1.34,-3,-3 S10.34,5,12,5z M12,19.2c-2.5,0,-4.71,-1.28,-6,-3.22c0.03,-1.99,4,-3.08,6,-3.08c1.99,0,5.97,1.09,6,3.08 C16.71,17.92,14.5,19.2,12,19.2z',
        viewBox: '0 0 24 24'
    },
    namespace: {
        path: 'M20,6h-8l-2,-2H4C2.9,4,2.01,4.9,2.01,6L2,18c0,1.1,0.9,2,2,2h16c1.1,0,2,-0.9,2,-2V8C22,6.9,21.1,6,20,6z M20,18H4V8h16V18z',
        viewBox: '0 0 24 24'
    }
};

// ============================================
// Configuration
// ============================================
const CONFIG = {
    refreshInterval: 3000,
    apiBaseUrl: '',
    diagramWidth: 900,
    diagramHeight: 650,
    maxAnimations: 20,
    animationDuration: 400,
    transitionDuration: 200
};

// ============================================
// State Management
// ============================================
let currentState = null;
let currentDiagram = null;
let previousDiagram = null;
let svg = null;
let tooltip = null;
let selectedNode = null;
let simulation = null;

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeDiagram();
    initializeTooltip();
    startAutoRefresh();
});

/**
 * Initialize the SVG diagram with gradients and zoom
 */
function initializeDiagram() {
    svg = d3.select('#architecture-diagram')
        .attr('width', CONFIG.diagramWidth)
        .attr('height', CONFIG.diagramHeight)
        .attr('viewBox', `0 0 ${CONFIG.diagramWidth} ${CONFIG.diagramHeight}`);

    // Create definitions for gradients
    const defs = svg.append('defs');
    createGradients(defs);

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on('zoom', (event) => {
            svg.select('.diagram-group').attr('transform', event.transform);
        });

    svg.call(zoom);

    // Create main group for diagram
    svg.append('g').attr('class', 'diagram-group');

    // Click outside to deselect
    svg.on('click', (event) => {
        if (event.target === svg.node()) {
            deselectAllNodes();
        }
    });
}

/**
 * Create radial gradients for node backgrounds
 */
function createGradients(defs) {
    const colors = {
        success: '#3FB950',
        warning: '#D29922',
        error: '#F85149',
        unknown: '#6E7681',
        primary: '#58A6FF'
    };

    Object.entries(colors).forEach(([name, color]) => {
        const gradient = defs.append('radialGradient')
            .attr('id', `gradient-${name}`)
            .attr('cx', '40%')
            .attr('cy', '40%');

        gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', d3.rgb(color).brighter(0.3));

        gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', color);
    });
}

/**
 * Initialize tooltip system
 */
function initializeTooltip() {
    tooltip = new Tooltip();
}

/**
 * Start auto-refresh polling
 */
function startAutoRefresh() {
    // Initial fetch
    fetchClusterState();
    fetchLevelDiagram();

    // Set up interval
    setInterval(() => {
        fetchClusterState();
    }, CONFIG.refreshInterval);

    // Re-fetch diagram every 30 seconds
    setInterval(() => {
        fetchLevelDiagram();
    }, 30000);
}

// ============================================
// API Calls
// ============================================

/**
 * Fetch current cluster state from API
 */
async function fetchClusterState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();

        const oldState = currentState;
        currentState = data;
        updateUI(data);
        updateDiagram(oldState);

    } catch (error) {
        console.error('Error fetching cluster state:', error);
    }
}

/**
 * Fetch level diagram configuration from API
 */
async function fetchLevelDiagram() {
    try {
        const response = await fetch('/api/level-diagram');
        const data = await response.json();

        // Only update if diagram actually changed
        if (JSON.stringify(data) !== JSON.stringify(currentDiagram)) {
            currentDiagram = data;
            updateDiagram();
        }

    } catch (error) {
        console.error('Error fetching diagram:', error);
    }
}

// ============================================
// UI Update Functions
// ============================================

/**
 * Update UI elements with current state
 */
function updateUI(data) {
    // Update game info
    const game = data.game || {};
    document.getElementById('world-level').textContent =
        `${game.current_world || 'World 1'} - ${game.current_level || 'Level 1'}`;
    document.getElementById('xp-display').textContent =
        `${game.total_xp || 0} XP`;

    // Update cluster stats
    const cluster = data.cluster || {};
    updatePodsList(cluster.pods || []);
    updateServicesList(cluster.services || []);
    updateDeploymentsList(cluster.deployments || []);
    updateOtherResources(cluster);

    // Update issues panel
    updateIssuesPanel(cluster);

    // Update last update time
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleTimeString();

    // Update status indicator
    const hasIssues = detectIssues(cluster).length > 0;
    const indicator = document.getElementById('status-indicator');
    indicator.className = 'status-indicator ' + (hasIssues ? 'error' : '');
}

/**
 * Helper to create elements
 */
function createElement(tag, className, text) {
    const elem = document.createElement(tag);
    if (className) elem.className = className;
    if (text) elem.textContent = text;
    return elem;
}

/**
 * Update pods list
 */
function updatePodsList(pods) {
    const container = document.getElementById('pods-list');
    container.textContent = '';

    if (pods.length === 0) {
        container.appendChild(createElement('div', 'no-resources', 'No pods found'));
        return;
    }

    pods.forEach(pod => {
        const div = createElement('div', 'resource-item');
        div.setAttribute('role', 'listitem');

        const header = createElement('div', 'resource-header');
        const statusClass = getStatusClass(pod.status, pod.ready);
        const statusBadge = createElement('span', `status-badge ${statusClass}`, pod.status);
        const name = createElement('span', 'resource-name', pod.name);

        header.appendChild(statusBadge);
        header.appendChild(name);
        div.appendChild(header);

        if (pod.restarts > 0 || pod.issues) {
            const meta = createElement('div', 'resource-meta');

            if (pod.restarts > 0) {
                const restartItem = createElement('span', 'meta-item');
                const icon = createElement('span', 'meta-icon', '🔄');
                restartItem.appendChild(icon);
                restartItem.appendChild(document.createTextNode(` ${pod.restarts} restarts`));
                meta.appendChild(restartItem);
            }

            div.appendChild(meta);
        }

        if (pod.issues && pod.issues.length > 0) {
            const issuesDiv = createElement('div', 'resource-issues');
            pod.issues.forEach(issue => {
                const issueText = createElement('div', '', `⚠ ${issue}`);
                issuesDiv.appendChild(issueText);
            });
            div.appendChild(issuesDiv);
        }

        container.appendChild(div);
    });
}

/**
 * Update services list
 */
function updateServicesList(services) {
    const container = document.getElementById('services-list');
    container.textContent = '';

    if (services.length === 0) {
        container.appendChild(createElement('div', 'no-resources', 'No services found'));
        return;
    }

    services.forEach(svc => {
        const div = createElement('div', 'resource-item');
        div.setAttribute('role', 'listitem');

        const header = createElement('div', 'resource-header');
        const hasIssues = svc.issues && svc.issues.length > 0;
        const statusClass = hasIssues ? 'error' : 'healthy';

        const statusBadge = createElement('span', `status-badge ${statusClass}`, svc.type);
        const name = createElement('span', 'resource-name', svc.name);

        header.appendChild(statusBadge);
        header.appendChild(name);
        div.appendChild(header);

        const meta = createElement('div', 'resource-meta');
        const epItem = createElement('span', 'meta-item');
        const icon = createElement('span', 'meta-icon', '🎯');
        epItem.appendChild(icon);
        epItem.appendChild(document.createTextNode(` ${svc.endpoints} endpoints`));
        meta.appendChild(epItem);
        div.appendChild(meta);

        if (hasIssues) {
            const issuesDiv = createElement('div', 'resource-issues');
            svc.issues.forEach(issue => {
                const issueText = createElement('div', '', `⚠ ${issue}`);
                issuesDiv.appendChild(issueText);
            });
            div.appendChild(issuesDiv);
        }

        container.appendChild(div);
    });
}

/**
 * Update deployments list
 */
function updateDeploymentsList(deployments) {
    const container = document.getElementById('deployments-list');
    container.textContent = '';

    if (deployments.length === 0) {
        container.appendChild(createElement('div', 'no-resources', 'No deployments found'));
        return;
    }

    deployments.forEach(deploy => {
        const div = createElement('div', 'resource-item');
        div.setAttribute('role', 'listitem');

        const header = createElement('div', 'resource-header');
        const isHealthy = deploy.ready_replicas === deploy.replicas;
        const statusClass = isHealthy ? 'healthy' : 'warning';

        const statusBadge = createElement('span', `status-badge ${statusClass}`,
            `${deploy.ready_replicas}/${deploy.replicas}`);
        const name = createElement('span', 'resource-name', deploy.name);

        header.appendChild(statusBadge);
        header.appendChild(name);
        div.appendChild(header);

        if (deploy.issues && deploy.issues.length > 0) {
            const issuesDiv = createElement('div', 'resource-issues');
            deploy.issues.forEach(issue => {
                const issueText = createElement('div', '', `⚠ ${issue}`);
                issuesDiv.appendChild(issueText);
            });
            div.appendChild(issuesDiv);
        }

        container.appendChild(div);
    });
}

/**
 * Update other resources section
 */
function updateOtherResources(cluster) {
    const container = document.getElementById('other-resources');
    container.textContent = '';

    const resources = [
        { name: 'ConfigMaps', data: cluster.configmaps || [] },
        { name: 'Secrets', data: cluster.secrets || [] },
        { name: 'Ingresses', data: cluster.ingresses || [] },
        { name: 'NetworkPolicies', data: cluster.networkpolicies || [] },
        { name: 'PVCs', data: cluster.pvcs || [] },
        { name: 'StatefulSets', data: cluster.statefulsets || [] }
    ];

    resources.forEach(resource => {
        if (resource.data.length > 0) {
            const div = createElement('div', 'resource-summary');
            div.setAttribute('role', 'listitem');
            const count = createElement('span', 'resource-count', resource.data.length.toString());
            const type = createElement('span', 'resource-type', resource.name);
            div.appendChild(count);
            div.appendChild(type);
            container.appendChild(div);
        }
    });

    if (container.children.length === 0) {
        container.appendChild(createElement('div', 'no-resources', 'No other resources'));
    }
}

/**
 * Update issues panel
 */
function updateIssuesPanel(cluster) {
    const container = document.getElementById('issues-list');
    const issues = detectIssues(cluster);

    container.textContent = '';

    if (issues.length === 0) {
        container.appendChild(createElement('div', 'no-issues', '✅ All systems operational!'));
        return;
    }

    issues.forEach(issue => {
        const div = createElement('div', `issue-item severity-${issue.severity}`);

        const icon = createElement('span', 'issue-icon',
            issue.severity === 'high' ? '🔴' : '🟡');
        const content = createElement('div', 'issue-content');
        const title = createElement('div', 'issue-title', issue.title);
        const description = createElement('div', 'issue-description', issue.description);

        content.appendChild(title);
        content.appendChild(description);
        div.appendChild(icon);
        div.appendChild(content);
        container.appendChild(div);
    });
}

/**
 * Detect issues from cluster state
 */
function detectIssues(cluster) {
    const issues = [];

    // Check pods
    (cluster.pods || []).forEach(pod => {
        if (pod.issues && pod.issues.length > 0) {
            pod.issues.forEach(issue => {
                issues.push({
                    severity: pod.status === 'Failed' ? 'high' : 'medium',
                    title: `Pod ${pod.name}`,
                    description: issue
                });
            });
        }
    });

    // Check services
    (cluster.services || []).forEach(svc => {
        if (svc.issues && svc.issues.length > 0) {
            svc.issues.forEach(issue => {
                issues.push({
                    severity: 'medium',
                    title: `Service ${svc.name}`,
                    description: issue
                });
            });
        }
    });

    // Check deployments
    (cluster.deployments || []).forEach(deploy => {
        if (deploy.issues && deploy.issues.length > 0) {
            deploy.issues.forEach(issue => {
                issues.push({
                    severity: deploy.ready_replicas === 0 ? 'high' : 'medium',
                    title: `Deployment ${deploy.name}`,
                    description: issue
                });
            });
        }
    });

    return issues;
}

/**
 * Get status class for badges
 */
function getStatusClass(status, ready) {
    if (status === 'Running' && ready) return 'healthy';
    if (status === 'Pending') return 'warning';
    if (status === 'Failed' || status === 'CrashLoopBackOff' || status === 'ImagePullBackOff') return 'error';
    return 'unknown';
}

// ============================================
// Diagram Update Functions
// ============================================

/**
 * Update the architecture diagram
 */
function updateDiagram(oldState = null) {
    if (!currentDiagram || !currentState) {
        return;
    }

    // Update diagram title
    const titleElem = document.getElementById('diagram-title');
    titleElem.textContent = '';
    const h2 = createElement('h2', null, currentDiagram.title || 'Architecture Diagram');
    titleElem.appendChild(h2);

    // Check if diagram structure has changed
    const diagramChanged = hasDiagramChanged(previousDiagram, currentDiagram);

    if (diagramChanged) {
        // Full redraw needed - diagram structure changed
        fullDiagramRedraw();
        previousDiagram = JSON.parse(JSON.stringify(currentDiagram));
    } else {
        // Only update node statuses - preserve interactions
        updateNodeStatuses();
    }
}

/**
 * Check if diagram structure has changed
 */
function hasDiagramChanged(prev, curr) {
    if (!prev) return true;
    if (!curr) return false;

    // Check if node count or IDs changed
    const prevNodes = (prev.nodes || []).map(n => n.id).sort().join(',');
    const currNodes = (curr.nodes || []).map(n => n.id).sort().join(',');
    if (prevNodes !== currNodes) return true;

    // Check if connections changed
    const prevConns = (prev.connections || []).map(c => `${c.from}-${c.to}`).sort().join(',');
    const currConns = (curr.connections || []).map(c => `${c.from}-${c.to}`).sort().join(',');
    if (prevConns !== currConns) return true;

    return false;
}

/**
 * Full diagram redraw (when structure changes)
 */
function fullDiagramRedraw() {
    const g = svg.select('.diagram-group');

    // Save selection state
    const savedSelection = selectedNode;

    // Fade out before update
    g.transition()
        .duration(150)
        .style('opacity', 0.6)
        .on('end', () => {
            g.selectAll('*').remove();

            // Draw new diagram
            drawConnections(g, currentDiagram.connections || []);
            drawNodes(g, currentDiagram.nodes || []);

            // Fade back in
            g.transition()
                .duration(150)
                .style('opacity', 1)
                .on('end', () => {
                    // Restore selection if it still exists
                    if (savedSelection) {
                        const nodeStillExists = (currentDiagram.nodes || []).some(n => n.id === savedSelection);
                        if (nodeStillExists) {
                            selectedNode = savedSelection;
                            highlightConnections(savedSelection);
                        }
                    }
                });
        });
}

/**
 * Update only node statuses (when diagram structure is same)
 */
function updateNodeStatuses() {
    if (!currentDiagram || !currentDiagram.nodes) return;

    // Update each node's visual status without redrawing
    currentDiagram.nodes.forEach((node, i) => {
        const status = getNodeStatus(node);
        const color = getNodeColor(status);

        // Find the node group by index (approximate - could be improved with data binding)
        const nodeGroups = svg.selectAll('.node').nodes();

        if (node.type === 'pod-group') {
            // Update pod group status
            updatePodGroupStatus(node, status, color);
        } else {
            // Update single node status
            updateSingleNodeStatus(node, status, color, i);
        }
    });
}

/**
 * Update single node status
 */
function updateSingleNodeStatus(node, status, color, index) {
    const gradientId = getGradientForStatus(status);

    // Select all nodes and filter to the one at this position
    svg.selectAll('.node')
        .filter(function() {
            const transform = d3.select(this).attr('transform');
            return transform && transform.includes(`translate(${node.x}, ${node.y})`);
        })
        .each(function() {
            const nodeGroup = d3.select(this);

            // Update glow color
            nodeGroup.select('.node-glow')
                .transition()
                .duration(300)
                .attr('stroke', color);

            // Update shape color
            const shape = nodeGroup.select('.node-shape');
            if (shape.node()) {
                if (shape.node().tagName === 'circle' || shape.node().tagName === 'rect') {
                    shape.transition()
                        .duration(300)
                        .attr('fill', `url(#${gradientId})`)
                        .attr('stroke', color);
                }
            }

            // Update or remove status indicator
            const existingIndicator = nodeGroup.select('circle[cx="30"]');
            if (status !== 'healthy') {
                const indicatorColor = status === 'error' ? '#F85149' : '#D29922';
                if (existingIndicator.empty()) {
                    // Add indicator
                    nodeGroup.append('circle')
                        .attr('cx', 30)
                        .attr('cy', -25)
                        .attr('r', 6)
                        .attr('fill', indicatorColor)
                        .attr('stroke', 'white')
                        .attr('stroke-width', 2)
                        .style('opacity', 0)
                        .transition()
                        .duration(200)
                        .style('opacity', 1);
                } else {
                    // Update existing indicator
                    existingIndicator
                        .transition()
                        .duration(300)
                        .attr('fill', indicatorColor);
                }
            } else if (!existingIndicator.empty()) {
                // Remove indicator
                existingIndicator
                    .transition()
                    .duration(200)
                    .style('opacity', 0)
                    .remove();
            }
        });
}

/**
 * Update pod group status
 */
function updatePodGroupStatus(node, status, color) {
    const gradientId = getGradientForStatus(status);
    const count = node.count || 3;
    const spacing = 45;
    const startX = node.x - ((count - 1) * spacing) / 2;

    for (let i = 0; i < count; i++) {
        const x = startX + (i * spacing);

        svg.selectAll('.pod-node')
            .filter(function() {
                const transform = d3.select(this).attr('transform');
                return transform && transform.includes(`translate(${x}, ${node.y})`);
            })
            .each(function() {
                const podGroup = d3.select(this);

                podGroup.select('.node-shape')
                    .transition()
                    .duration(300)
                    .attr('fill', `url(#${gradientId})`)
                    .attr('stroke', color);
            });
    }
}

/**
 * Draw connections between nodes
 */
function drawConnections(g, connections) {
    const nodePositions = getNodePositions();

    connections.forEach((conn, i) => {
        const from = nodePositions[conn.from];
        const to = nodePositions[conn.to];

        if (!from || !to) return;

        // Calculate path
        const line = g.append('line')
            .attr('x1', from.x)
            .attr('y1', from.y)
            .attr('x2', to.x)
            .attr('y2', to.y)
            .attr('class', `connection-line conn-${conn.from} conn-${conn.to}`)
            .attr('stroke-dasharray', '5,5')
            .attr('id', `conn-${i}`);

        // Animate line drawing
        animateConnectionDraw(line);

        // Draw label if exists
        if (conn.label) {
            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;

            g.append('text')
                .attr('x', midX)
                .attr('y', midY - 5)
                .attr('class', 'connection-label')
                .style('opacity', 0)
                .text(conn.label)
                .transition()
                .delay(300)
                .duration(200)
                .style('opacity', 1);
        }
    });
}

/**
 * Animate connection line drawing
 */
function animateConnectionDraw(line) {
    const length = line.node().getTotalLength();

    line
        .attr('stroke-dasharray', `${length} ${length}`)
        .attr('stroke-dashoffset', length)
        .transition()
        .duration(800)
        .ease(d3.easeCubicInOut)
        .attr('stroke-dashoffset', 0)
        .on('end', function() {
            // Reset to dashed line style
            d3.select(this).attr('stroke-dasharray', '5,5');
        });
}

/**
 * Draw nodes on the diagram
 */
function drawNodes(g, nodes) {
    nodes.forEach((node, i) => {
        const status = getNodeStatus(node);
        const color = getNodeColor(status);
        const gradientId = getGradientForStatus(status);

        // Draw node based on type
        if (node.type === 'pod-group') {
            drawPodGroup(g, node, status, i);
        } else {
            drawEnhancedNode(g, node, color, gradientId, status, i);
        }
    });
}

/**
 * Draw enhanced node with SVG icon
 */
function drawEnhancedNode(g, node, color, gradientId, status, index) {
    const nodeGroup = g.append('g')
        .attr('class', 'node')
        .attr('transform', `translate(${node.x}, ${node.y})`)
        .attr('tabindex', 0)
        .attr('role', 'button')
        .attr('aria-label', `${node.type}: ${node.label}`)
        .style('opacity', 0)
        .on('click', (event) => handleNodeClick(event, node))
        .on('mouseenter', (event) => handleNodeHover(event, node, true))
        .on('mouseleave', (event) => handleNodeHover(event, node, false));

    // Background glow
    nodeGroup.append('circle')
        .attr('r', 45)
        .attr('class', 'node-glow')
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', 0)
        .attr('opacity', 0.2);

    // Main shape with gradient
    const shape = getNodeShape(node.type);
    if (shape === 'cylinder') {
        drawCylinder(nodeGroup, color);
    } else if (shape === 'rect') {
        nodeGroup.append('rect')
            .attr('x', -40)
            .attr('y', -30)
            .attr('width', 80)
            .attr('height', 60)
            .attr('rx', 8)
            .attr('class', 'node-shape')
            .attr('fill', `url(#${gradientId})`)
            .attr('stroke', color)
            .attr('stroke-width', 2);
    } else {
        nodeGroup.append('circle')
            .attr('r', 35)
            .attr('class', 'node-shape')
            .attr('fill', `url(#${gradientId})`)
            .attr('stroke', color)
            .attr('stroke-width', 2);
    }

    // SVG Icon
    const icon = K8S_ICONS[node.type] || K8S_ICONS.pod;
    nodeGroup.append('path')
        .attr('d', icon.path)
        .attr('transform', 'translate(-12, -12) scale(1)')
        .attr('fill', 'white')
        .attr('class', 'node-icon')
        .attr('opacity', 0.95);

    // Label
    nodeGroup.append('text')
        .attr('y', 55)
        .attr('class', 'node-label')
        .text(truncateLabel(node.label, 20));

    // Status indicator for errors/warnings
    if (status !== 'healthy') {
        const indicatorColor = status === 'error' ? '#F85149' : '#D29922';
        nodeGroup.append('circle')
            .attr('cx', 30)
            .attr('cy', -25)
            .attr('r', 6)
            .attr('fill', indicatorColor)
            .attr('stroke', 'white')
            .attr('stroke-width', 2)
            .style('opacity', 0)
            .transition()
            .delay(index * 50 + 400)
            .duration(200)
            .style('opacity', 1);
    }

    // Entrance animation
    nodeGroup
        .transition()
        .delay(index * 50)
        .duration(CONFIG.animationDuration)
        .ease(d3.easeBackOut)
        .style('opacity', 1);
}

/**
 * Draw pod group (multiple pods)
 */
function drawPodGroup(g, node, status, groupIndex) {
    const count = node.count || 3;
    const spacing = 45;
    const startX = node.x - ((count - 1) * spacing) / 2;

    for (let i = 0; i < count; i++) {
        const color = getNodeColor(status);
        const gradientId = getGradientForStatus(status);
        const x = startX + (i * spacing);

        const podGroup = g.append('g')
            .attr('class', 'node pod-node')
            .attr('transform', `translate(${x}, ${node.y})`)
            .attr('tabindex', 0)
            .attr('role', 'button')
            .attr('aria-label', `Pod ${i + 1} of ${count}`)
            .style('opacity', 0)
            .on('click', (event) => handleNodeClick(event, node))
            .on('mouseenter', (event) => handleNodeHover(event, node, true))
            .on('mouseleave', (event) => handleNodeHover(event, node, false));

        podGroup.append('rect')
            .attr('x', -18)
            .attr('y', -18)
            .attr('width', 36)
            .attr('height', 36)
            .attr('rx', 4)
            .attr('class', 'node-shape')
            .attr('fill', `url(#${gradientId})`)
            .attr('stroke', color)
            .attr('stroke-width', 2);

        // Icon
        const icon = K8S_ICONS.pod;
        podGroup.append('path')
            .attr('d', icon.path)
            .attr('transform', 'translate(-9, -9) scale(0.75)')
            .attr('fill', 'white')
            .attr('opacity', 0.95);

        // Entrance animation
        podGroup
            .transition()
            .delay(groupIndex * 50 + i * 30)
            .duration(CONFIG.animationDuration)
            .ease(d3.easeBackOut)
            .style('opacity', 1);
    }

    // Label below group
    g.append('text')
        .attr('x', node.x)
        .attr('y', node.y + 40)
        .attr('class', 'node-label')
        .attr('text-anchor', 'middle')
        .style('opacity', 0)
        .text(truncateLabel(node.label, 20))
        .transition()
        .delay(groupIndex * 50)
        .duration(200)
        .style('opacity', 1);
}

/**
 * Draw cylinder shape for databases/storage
 */
function drawCylinder(g, color) {
    const width = 70;
    const height = 50;
    const ellipseRy = 12;

    // Top ellipse
    g.append('ellipse')
        .attr('cx', 0)
        .attr('cy', -height/2 + ellipseRy)
        .attr('rx', width/2)
        .attr('ry', ellipseRy)
        .attr('fill', color)
        .attr('stroke', d3.rgb(color).darker(0.5))
        .attr('stroke-width', 2);

    // Body
    g.append('rect')
        .attr('x', -width/2)
        .attr('y', -height/2 + ellipseRy)
        .attr('width', width)
        .attr('height', height - ellipseRy)
        .attr('fill', color)
        .attr('stroke', 'none');

    // Bottom ellipse
    g.append('ellipse')
        .attr('cx', 0)
        .attr('cy', height/2)
        .attr('rx', width/2)
        .attr('ry', ellipseRy)
        .attr('fill', d3.rgb(color).darker(0.3))
        .attr('stroke', d3.rgb(color).darker(0.5))
        .attr('stroke-width', 2);

    // Side lines
    g.append('line')
        .attr('x1', -width/2)
        .attr('y1', -height/2 + ellipseRy)
        .attr('x2', -width/2)
        .attr('y2', height/2)
        .attr('stroke', d3.rgb(color).darker(0.5))
        .attr('stroke-width', 2);

    g.append('line')
        .attr('x1', width/2)
        .attr('y1', -height/2 + ellipseRy)
        .attr('x2', width/2)
        .attr('y2', height/2)
        .attr('stroke', d3.rgb(color).darker(0.5))
        .attr('stroke-width', 2);
}

// ============================================
// Helper Functions
// ============================================

/**
 * Get node positions for connections
 */
function getNodePositions() {
    if (!currentDiagram) return {};

    const positions = {};
    (currentDiagram.nodes || []).forEach(node => {
        positions[node.id] = { x: node.x, y: node.y };
    });

    return positions;
}

/**
 * Get node status based on cluster state
 */
function getNodeStatus(node) {
    if (!currentState || !currentState.cluster) return 'unknown';

    const cluster = currentState.cluster;

    // Check pods
    if (node.type === 'pod' || node.type === 'pod-group') {
        const pods = cluster.pods || [];
        const unhealthyPods = pods.filter(p =>
            p.status !== 'Running' || !p.ready || (p.issues && p.issues.length > 0)
        );
        if (unhealthyPods.length > 0) return 'error';
        if (pods.length === 0) return 'unknown';
        return 'healthy';
    }

    // Check services
    if (node.type === 'service') {
        const services = cluster.services || [];
        const svc = services.find(s => node.resource_name ? s.name === node.resource_name : true);
        if (svc && svc.issues && svc.issues.length > 0) return 'error';
        if (svc && svc.endpoints === 0) return 'warning';
        if (services.length === 0) return 'unknown';
        return 'healthy';
    }

    // Check deployments
    if (node.type === 'deployment') {
        const deployments = cluster.deployments || [];
        const deploy = deployments.find(d => node.resource_name ? d.name === node.resource_name : true);
        if (deploy && deploy.ready_replicas < deploy.replicas) return 'warning';
        if (deploy && deploy.ready_replicas === 0) return 'error';
        if (deployments.length === 0) return 'unknown';
        return 'healthy';
    }

    return 'healthy';
}

/**
 * Get color based on status
 */
function getNodeColor(status) {
    switch (status) {
        case 'healthy': return '#3FB950';
        case 'warning': return '#D29922';
        case 'error': return '#F85149';
        default: return '#6E7681';
    }
}

/**
 * Get gradient ID for status
 */
function getGradientForStatus(status) {
    switch (status) {
        case 'healthy': return 'gradient-success';
        case 'warning': return 'gradient-warning';
        case 'error': return 'gradient-error';
        default: return 'gradient-unknown';
    }
}

/**
 * Get node shape based on type
 */
function getNodeShape(type) {
    if (['statefulset', 'pvc'].includes(type)) return 'cylinder';
    if (['deployment', 'service', 'configmap', 'secret'].includes(type)) return 'rect';
    return 'circle';
}

/**
 * Truncate label to max length
 */
function truncateLabel(label, maxLen) {
    if (!label) return '';
    if (label.length <= maxLen) return label;
    return label.substring(0, maxLen - 3) + '...';
}

// ============================================
// Interactivity Handlers
// ============================================

/**
 * Handle node click
 */
function handleNodeClick(event, node) {
    event.stopPropagation();

    // Toggle selection
    if (selectedNode === node.id) {
        deselectAllNodes();
    } else {
        deselectAllNodes();
        selectNode(node.id);
        highlightConnections(node.id);
    }
}

/**
 * Handle node hover
 */
function handleNodeHover(event, node, isEntering) {
    if (isEntering) {
        // Show tooltip
        const tooltipContent = createTooltipContent(node);
        tooltip.show(tooltipContent, event);
    } else {
        // Hide tooltip
        tooltip.hide();
    }
}

/**
 * Create tooltip content for a node (safe DOM methods)
 */
function createTooltipContent(node) {
    const type = node.type.charAt(0).toUpperCase() + node.type.slice(1);
    const status = getNodeStatus(node);

    // Create tooltip structure using DOM methods
    const container = createElement('div', 'tooltip-content');

    const header = createElement('div', 'tooltip-header');
    const icon = createElement('span', 'tooltip-icon', getNodeIcon(node.type));
    const title = createElement('strong', null, `${type}: ${node.label}`);
    header.appendChild(icon);
    header.appendChild(title);

    const body = createElement('div', 'tooltip-body');

    const statusRow = createElement('div', 'tooltip-row');
    const statusLabel = createElement('span', 'tooltip-label', 'Status:');
    const statusValue = createElement('span', 'tooltip-value', status);
    statusRow.appendChild(statusLabel);
    statusRow.appendChild(statusValue);

    const typeRow = createElement('div', 'tooltip-row');
    const typeLabel = createElement('span', 'tooltip-label', 'Type:');
    const typeValue = createElement('span', 'tooltip-value', type);
    typeRow.appendChild(typeLabel);
    typeRow.appendChild(typeValue);

    body.appendChild(statusRow);
    body.appendChild(typeRow);

    const footer = createElement('div', 'tooltip-footer', 'Click to select and highlight connections');

    container.appendChild(header);
    container.appendChild(body);
    container.appendChild(footer);

    return container;
}

/**
 * Get icon emoji for node type
 */
function getNodeIcon(type) {
    const icons = {
        pod: '📦', deployment: '🚀', service: '⚖️', ingress: '🌐',
        configmap: '⚙️', secret: '🔐', networkpolicy: '🔒',
        statefulset: '💾', pvc: '💿', replicaset: '🔄',
        hpa: '📊', role: '🎭', namespace: '📁'
    };
    return icons[type] || '📦';
}

/**
 * Select a node
 */
function selectNode(nodeId) {
    selectedNode = nodeId;
    svg.selectAll('.node')
        .filter(function() {
            const transform = d3.select(this).attr('transform');
            // This is a simple selection - in production you'd track node IDs better
            return false;
        })
        .classed('selected', true);
}

/**
 * Deselect all nodes
 */
function deselectAllNodes() {
    selectedNode = null;
    svg.selectAll('.node').classed('selected', false);
    svg.selectAll('.connection-line')
        .classed('highlighted', false)
        .classed('dimmed', false);
}

/**
 * Highlight connections related to a node
 */
function highlightConnections(nodeId) {
    // Dim all connections
    svg.selectAll('.connection-line')
        .classed('dimmed', true)
        .classed('highlighted', false);

    // Highlight related connections
    svg.selectAll(`.conn-${nodeId}`)
        .classed('dimmed', false)
        .classed('highlighted', true);
}

// ============================================
// Tooltip Class
// ============================================

class Tooltip {
    constructor() {
        this.element = d3.select('#tooltip');
    }

    show(contentElement, event) {
        // Clear existing content
        this.element.node().textContent = '';

        // Append the new content element
        this.element.node().appendChild(contentElement);

        this.element
            .style('left', `${event.pageX + 12}px`)
            .style('top', `${event.pageY - 12}px`)
            .style('opacity', 1);
    }

    hide() {
        this.element
            .style('opacity', 0);
    }
}
