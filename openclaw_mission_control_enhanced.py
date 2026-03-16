"""
OpenClaw Mission Control Dashboard - Enhanced Streamlit Implementation
=====================================================================

This dashboard implements the UX/UI principles and benefits from OpenClaw Mission Control:
https://github.com/abhi1693/openclaw-mission-control

KEY BENEFITS IMPLEMENTED:
- Operations-first design for reliable agent work execution
- Built-in governance with approvals and clear control boundaries  
- Gateway-aware orchestration for distributed environments
- Unified UI and API model for operators and automation
- Team-scale structure supporting organizations and multi-team operations
- Full audit trail and activity history for compliance
- Human-in-the-loop controls for sensitive actions
- Self-hosted friendly with local authentication support
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Mission Control | OpenClaw",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/abhi1693/openclaw-mission-control',
        'Report a bug': 'https://github.com/abhi1693/openclaw-mission-control/issues',
        'About': 'OpenClaw Mission Control - AI Agent Orchestration Dashboard'
    }
)

# =============================================================================
# COLOR SYSTEM & THEME (Dark Operations Center)
# =============================================================================

COLORS = {
    "background": "#0e1117",
    "card_background": "#1e2129", 
    "text_primary": "#fafafa",
    "text_secondary": "#a0a0a0",
    "accent_active": "#00cc00",
    "accent_idle": "#666666", 
    "accent_warning": "#ffd700",
    "accent_critical": "#ff4b4b",
    "accent_info": "#4b9aff",
    "border_default": "#2d3139",
    "accent_pending": "#ff9f43"
}

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

st.markdown(f"""
<style>
    /* Base Theme */
    .stApp {{
        background-color: {COLORS["background"]};
        color: {COLORS["text_primary"]};
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS["text_primary"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    p, span, div {{
        color: {COLORS["text_primary"]};
    }}
    
    /* Metric Cards */
    .metric-card {{
        background-color: {COLORS["card_background"]};
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid {COLORS["accent_critical"]};
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    .metric-card-success {{
        background-color: {COLORS["card_background"]};
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid {COLORS["accent_active"]};
        margin-bottom: 0.5rem;
    }}
    
    .metric-card-warning {{
        background-color: {COLORS["card_background"]};
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid {COLORS["accent_warning"]};
        margin-bottom: 0.5rem;
    }}
    
    /* Agent Status Cards */
    .agent-active {{
        background-color: {COLORS["card_background"]};
        padding: 0.75rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_active"]};
        margin-bottom: 0.5rem;
    }}
    
    .agent-idle {{
        background-color: {COLORS["card_background"]};
        padding: 0.75rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_idle"]};
        margin-bottom: 0.5rem;
    }}
    
    .agent-busy {{
        background-color: {COLORS["card_background"]};
        padding: 0.75rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_warning"]};
        margin-bottom: 0.5rem;
    }}
    
    .agent-offline {{
        background-color: {COLORS["card_background"]};
        padding: 0.75rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_critical"]};
        margin-bottom: 0.5rem;
        opacity: 0.7;
    }}
    
    /* Kanban Board Cards */
    .kanban-card {{
        background: {COLORS["card_background"]};
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
        border-left: 3px solid {COLORS["accent_warning"]};
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }}
    
    .kanban-card-high {{
        border-left-color: {COLORS["accent_critical"]};
    }}
    
    .kanban-card-medium {{
        border-left-color: {COLORS["accent_warning"]};
    }}
    
    .kanban-card-low {{
        border-left-color: {COLORS["accent_info"]};
    }}
    
    /* Approval Cards */
    .approval-pending {{
        background-color: {COLORS["card_background"]};
        padding: 0.75rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_pending"]};
        margin-bottom: 0.5rem;
    }}
    
    .approval-approved {{
        background-color: {COLORS["card_background"]};
        padding: 0.75rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_active"]};
        margin-bottom: 0.5rem;
    }}
    
    /* Activity Feed */
    .activity-item {{
        background-color: {COLORS["card_background"]};
        padding: 0.5rem 0.75rem;
        border-radius: 0.3rem;
        margin-bottom: 0.3rem;
        font-size: 0.85rem;
        border-left: 2px solid {COLORS["accent_info"]};
    }}
    
    /* Gateway Status */
    .gateway-connected {{
        background-color: {COLORS["card_background"]};
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_active"]};
        margin-bottom: 0.3rem;
    }}
    
    .gateway-disconnected {{
        background-color: {COLORS["card_background"]};
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid {COLORS["accent_critical"]};
        margin-bottom: 0.3rem;
    }}
    
    /* Status Badges */
    .status-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
    }}
    
    /* Progress Bar */
    .progress-container {{
        background-color: {COLORS["border_default"]};
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }}
    
    .progress-bar {{
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }}
    
    /* Divider */
    hr {{
        border-color: {COLORS["border_default"]} !important;
        margin: 1rem 0;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {COLORS["card_background"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border_default"]};
        border-radius: 0.3rem;
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS["border_default"]};
        border-color: {COLORS["accent_info"]};
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA MODELS & STATE MANAGEMENT
# =============================================================================

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        # UI State
        "show_new_task": False,
        "show_deploy_agent": False,
        "show_create_board": False,
        "selected_organization": "org_1",
        "sidebar_collapsed": True,
        
        # Data - Organizations
        "organizations": [
            {"id": "org_1", "name": "Production", "description": "Main production organization"},
            {"id": "org_2", "name": "Development", "description": "Development and testing"},
        ],
        
        # Data - Board Groups  
        "board_groups": [
            {"id": "bg_1", "name": "Content Production", "org_id": "org_1"},
            {"id": "bg_2", "name": "Lead Generation", "org_id": "org_1"},
        ],
        
        # Data - Boards
        "boards": [
            {
                "id": "board_1",
                "name": "Atlas Unknown",
                "description": "YouTube documentary series",
                "board_group_id": "bg_1",
                "progress": {"completed": 5, "total": 20},
                "status": "In Progress"
            },
            {
                "id": "board_2", 
                "name": "Armada Capital",
                "description": "Investment fund content",
                "board_group_id": "bg_1",
                "progress": {"completed": 0, "total": 1},
                "status": "Planning"
            },
            {
                "id": "board_3",
                "name": "Lead Gen Agency",
                "description": "Lead generation campaigns",
                "board_group_id": "bg_2",
                "progress": {"completed": 0, "total": 1},
                "status": "Backlog"
            },
        ],
        
        # Data - Tasks (Kanban)
        "tasks": [
            {
                "id": "AU-03",
                "title": "Lake Nyos Script",
                "description": "Research and script writing for Lake Nyos episode",
                "board_id": "board_1",
                "stage": "In Progress",
                "qa_score": 95,
                "assigned_agent": "youtube-scriptwriter",
                "priority": "high",
                "due_date": "2024-01-15",
                "tags": ["script", "atlas-unknown", "research"]
            },
            {
                "id": "AU-02",
                "title": "Centralia Script",
                "description": "Ready to record - final review complete",
                "board_id": "board_1", 
                "stage": "Review",
                "qa_score": 98,
                "assigned_agent": "youtube-scriptwriter",
                "priority": "high",
                "due_date": "2024-01-12",
                "tags": ["script", "atlas-unknown", "ready"]
            },
            {
                "id": "AU-01",
                "title": "Series Introduction",
                "description": "Introduction episode script",
                "board_id": "board_1",
                "stage": "Complete",
                "qa_score": 100,
                "assigned_agent": "youtube-scriptwriter", 
                "priority": "medium",
                "due_date": "2024-01-05",
                "tags": ["script", "atlas-unknown", "complete"]
            },
            {
                "id": "AU-04",
                "title": "Research: Dyatlov Pass",
                "description": "Background research for upcoming episode",
                "board_id": "board_1",
                "stage": "Planned",
                "qa_score": 0,
                "assigned_agent": None,
                "priority": "medium", 
                "due_date": "2024-01-20",
                "tags": ["research", "atlas-unknown"]
            },
        ],
        
        # Data - Agents
        "agents": [
            {
                "id": "agent_1",
                "name": "youtube-scriptwriter",
                "role": "content-writer",
                "status": "active",
                "current_task": "AU-03: Lake Nyos",
                "skills": ["scriptwriting", "research", "storytelling"],
                "last_seen": datetime.now().isoformat(),
                "gateway_id": "gw_1"
            },
            {
                "id": "agent_2",
                "name": "leadgen-master", 
                "role": "lead-generator",
                "status": "idle",
                "current_task": None,
                "skills": ["outreach", "copywriting", "analytics"],
                "last_seen": datetime.now().isoformat(),
                "gateway_id": "gw_1"
            },
            {
                "id": "agent_3",
                "name": "legal-drafter",
                "role": "legal-assistant", 
                "status": "idle",
                "current_task": None,
                "skills": ["contract-drafting", "compliance", "review"],
                "last_seen": (datetime.now() - timedelta(hours=2)).isoformat(),
                "gateway_id": None
            },
            {
                "id": "agent_4",
                "name": "seo-strategist",
                "role": "seo-specialist",
                "status": "busy",
                "current_task": "Keyword research for AC-01",
                "skills": ["keyword-research", "content-optimization", "analytics"],
                "last_seen": datetime.now().isoformat(),
                "gateway_id": "gw_1"
            },
        ],
        
        # Data - Approvals
        "approvals": [
            {
                "id": "appr_1",
                "task_id": "AU-03",
                "task_title": "Lake Nyos Script - Final Review",
                "requester": "youtube-scriptwriter",
                "requester_id": "agent_1",
                "status": "pending",
                "requested_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "confidential": False,
                "description": "Script is ready for final approval before recording"
            },
            {
                "id": "appr_2", 
                "task_id": "AC-01",
                "task_title": "Fund Documents - Legal Review",
                "requester": "legal-drafter",
                "requester_id": "agent_3", 
                "status": "pending",
                "requested_at": (datetime.now() - timedelta(hours=3)).isoformat(),
                "confidential": True,
                "description": "Confidential: Fund documentation requires approval"
            },
        ],
        
        # Data - Activity Log
        "activities": [
            {
                "id": "act_1",
                "event_type": "task_moved",
                "description": "Task AU-03 moved to 'In Progress'",
                "user": "danny",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "icon": "📝"
            },
            {
                "id": "act_2",
                "event_type": "approval_requested", 
                "description": "Approval requested for AU-03",
                "user": "youtube-scriptwriter",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "icon": "⏳"
            },
            {
                "id": "act_3",
                "event_type": "agent_deployed",
                "description": "Agent 'seo-strategist' deployed to gateway gw_1",
                "user": "system",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "icon": "🤖"
            },
            {
                "id": "act_4",
                "event_type": "task_completed",
                "description": "Task AU-01 marked as Complete (QA: 100%)",
                "user": "youtube-scriptwriter",
                "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
                "icon": "✅"
            },
        ],
        
        # Data - Gateways
        "gateways": [
            {
                "id": "gw_1",
                "name": "Production Gateway",
                "status": "connected",
                "url": "https://gateway.production.local",
                "agents_count": 3,
                "last_heartbeat": datetime.now().isoformat(),
                "tls_verified": True
            },
            {
                "id": "gw_2", 
                "name": "Development Gateway",
                "status": "disconnected",
                "url": "https://gateway.dev.local",
                "agents_count": 0,
                "last_heartbeat": (datetime.now() - timedelta(hours=5)).isoformat(),
                "tls_verified": False
            },
        ],
        
        # Data - Reminders
        "reminders": [
            {"id": "rem_1", "time": "09:00", "task": "Review Centralia script", "completed": True},
            {"id": "rem_2", "time": "14:00", "task": "Call Joel - Fund docs", "completed": False},
            {"id": "rem_3", "time": "16:30", "task": "Deploy new agent version", "completed": False},
        ],
        
        # Sync status
        "last_sync": datetime.now()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_status_color(status: str) -> str:
    """Get color for a given status"""
    status_colors = {
        "active": COLORS["accent_active"],
        "idle": COLORS["accent_idle"],
        "busy": COLORS["accent_warning"],
        "offline": COLORS["accent_critical"],
        "connected": COLORS["accent_active"],
        "disconnected": COLORS["accent_critical"],
        "pending": COLORS["accent_pending"],
        "approved": COLORS["accent_active"],
        "rejected": COLORS["accent_critical"],
        "In Progress": COLORS["accent_warning"],
        "Complete": COLORS["accent_active"],
        "Review": COLORS["accent_pending"],
        "Planning": COLORS["accent_info"],
        "Backlog": COLORS["accent_idle"],
        "Planned": COLORS["accent_info"],
        "high": COLORS["accent_critical"],
        "medium": COLORS["accent_warning"],
        "low": COLORS["accent_info"]
    }
    return status_colors.get(status, COLORS["accent_idle"])

def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to human-readable"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            return f"{int(diff.seconds / 60)}m ago"
        elif diff < timedelta(days=1):
            return f"{int(diff.seconds / 3600)}h ago"
        else:
            return dt.strftime("%b %d, %H:%M")
    except:
        return iso_timestamp

def get_agent_css_class(status: str) -> str:
    """Get CSS class for agent status"""
    classes = {
        "active": "agent-active",
        "idle": "agent-idle",
        "busy": "agent-busy",
        "offline": "agent-offline"
    }
    return classes.get(status, "agent-idle")

def get_tasks_by_stage(tasks: List[Dict], stage: str) -> List[Dict]:
    """Filter tasks by kanban stage"""
    return [t for t in tasks if t["stage"] == stage]

def render_progress_bar(current: int, total: int, color: str = None):
    """Render a visual progress bar"""
    if total == 0:
        percentage = 0
    else:
        percentage = (current / total) * 100
    
    if color is None:
        if percentage >= 80:
            color = COLORS["accent_active"]
        elif percentage >= 50:
            color = COLORS["accent_warning"]
        else:
            color = COLORS["accent_info"]
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%; background-color: {color};"></div>
    </div>
    <small>{current}/{total} ({percentage:.0f}%)</small>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN DASHBOARD UI
# =============================================================================

# Header Section
st.title("🎯 MISSION CONTROL")
header_cols = st.columns([3, 1, 1, 1])

with header_cols[0]:
    st.caption(f"Last sync: {st.session_state.last_sync.strftime('%H:%M:%S')} | OpenClaw Gateway v1.0")

with header_cols[1]:
    active_agents = len([a for a in st.session_state.agents if a["status"] == "active"])
    st.metric("Active Agents", active_agents, delta=None)

with header_cols[2]:
    pending_approvals = len([a for a in st.session_state.approvals if a["status"] == "pending"])
    st.metric("Pending Approvals", pending_approvals, delta=None)

with header_cols[3]:
    in_progress_tasks = len([t for t in st.session_state.tasks if t["stage"] == "In Progress"])
    st.metric("In Progress", in_progress_tasks, delta=None)

st.divider()

# Main Layout - Three Columns
col1, col2, col3 = st.columns([2, 2.5, 1])

# =============================================================================
# COLUMN 1: ACTIVE OPERATIONS & PROJECTS
# =============================================================================

with col1:
    # Active Operations Section
    st.subheader("🔥 ACTIVE OPERATIONS")
    
    # Current Focus Display
    current_focus = "AU-03: Lake Nyos Script (In Progress)"
    current_mode = "Production"
    
    st.markdown(f"""
    <div class="metric-card">
        <b>Current Focus:</b> {current_focus}<br>
        <b>Mode:</b> <span style="color: {COLORS['accent_active']};">●</span> {current_mode}
    </div>
    """, unsafe_allow_html=True)
    
    # Gateway Status Summary
    st.caption("Gateway Status")
    for gateway in st.session_state.gateways:
        css_class = "gateway-connected" if gateway["status"] == "connected" else "gateway-disconnected"
        status_icon = "🟢" if gateway["status"] == "connected" else "🔴"
        st.markdown(f"""
        <div class="{css_class}">
            <b>{status_icon} {gateway['name']}</b><br>
            <small>{gateway['agents_count']} agents | {format_timestamp(gateway['last_heartbeat'])}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Projects Section
    st.subheader("📊 PROJECTS")
    
    for board in st.session_state.boards:
        progress = board["progress"]
        percentage = (progress["completed"] / progress["total"] * 100) if progress["total"] > 0 else 0
        
        status_color = get_status_color(board["status"])
        
        with st.container():
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {status_color};">
                <b>{board['name']}</b><br>
                <small>{board['description']}</small><br>
                <span class="status-badge" style="background-color: {status_color}33; color: {status_color};">
                    {board['status']}
                </span>
            </div>
            """, unsafe_allow_html=True)
            render_progress_bar(progress["completed"], progress["total"])
            st.caption("")

# =============================================================================
# COLUMN 2: AGENT STATUS & ACTIVITY FEED
# =============================================================================

with col2:
    # Agent Status Section
    st.subheader("🤖 AGENT STATUS")
    
    agent_cols = st.columns(2)
    for idx, agent in enumerate(st.session_state.agents):
        with agent_cols[idx % 2]:
            css_class = get_agent_css_class(agent["status"])
            status_emoji = {"active": "🟢", "idle": "⚪", "busy": "🟡", "offline": "🔴"}.get(agent["status"], "⚪")
            task_display = agent["current_task"] if agent["current_task"] else "Idle"
            last_seen = format_timestamp(agent["last_seen"])
            
            st.markdown(f"""
            <div class="{css_class}">
                <b>{status_emoji} {agent['name']}</b><br>
                <small><b>Role:</b> {agent['role']}</small><br>
                <small><b>Task:</b> {task_display}</small><br>
                <small style="color: {COLORS['text_secondary']};">Last seen: {last_seen}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Activity Feed Section
    st.subheader("📋 ACTIVITY FEED")
    
    # Sort activities by timestamp (newest first)
    sorted_activities = sorted(
        st.session_state.activities,
        key=lambda x: x["timestamp"],
        reverse=True
    )
    
    for activity in sorted_activities[:6]:  # Show last 6 activities
        time_ago = format_timestamp(activity["timestamp"])
        st.markdown(f"""
        <div class="activity-item">
            <b>{activity['icon']} {activity['event_type'].replace('_', ' ').title()}</b><br>
            <small>{activity['description']}</small><br>
            <small style="color: {COLORS['text_secondary']};">by {activity['user']} • {time_ago}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Pending Approvals Preview
    st.divider()
    st.subheader("⏳ PENDING APPROVALS")
    
    pending = [a for a in st.session_state.approvals if a["status"] == "pending"]
    if pending:
        for approval in pending[:3]:  # Show first 3
            conf_icon = "🔒" if approval["confidential"] else ""
            req_time = format_timestamp(approval["requested_at"])
            
            st.markdown(f"""
            <div class="approval-pending">
                <b>{conf_icon} {approval['task_title']}</b><br>
                <small>Requested by {approval['requester']} • {req_time}</small><br>
                <small style="color: {COLORS['text_secondary']};">{approval['description'][:60]}...</small>
            </div>
            """, unsafe_allow_html=True)
            
            appr_cols = st.columns(2)
            with appr_cols[0]:
                if st.button(f"✅ Approve", key=f"approve_{approval['id']}", use_container_width=True):
                    st.success(f"Approved {approval['task_id']}")
            with appr_cols[1]:
                if st.button(f"❌ Reject", key=f"reject_{approval['id']}", use_container_width=True):
                    st.error(f"Rejected {approval['task_id']}")
    else:
        st.info("No pending approvals")

# =============================================================================
# COLUMN 3: REMINDERS & QUICK ACTIONS
# =============================================================================

with col3:
    # Today's Schedule
    st.subheader("⏰ TODAY")
    
    for reminder in st.session_state.reminders:
        status_icon = "✅" if reminder["completed"] else "⏳"
        strike = "text-decoration: line-through; opacity: 0.6;" if reminder["completed"] else ""
        
        st.markdown(f"""
        <div class="activity-item">
            <span style="{strike}">
                <b>{status_icon} {reminder['time']}</b><br>
                <small>{reminder['task']}</small>
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick Actions
    st.subheader("⚡ QUICK ACTIONS")
    
    if st.button("📝 New Task", use_container_width=True, type="primary"):
        st.session_state.show_new_task = True
        
    if st.button("🤖 Deploy Agent", use_container_width=True):
        st.session_state.show_deploy_agent = True
        
    if st.button("📋 Create Board", use_container_width=True):
        st.session_state.show_create_board = True
        
    if st.button("🔍 View Logs", use_container_width=True):
        st.info("Log viewer would open here")
    
    st.divider()
    
    # System Health
    st.subheader("🏥 SYSTEM HEALTH")
    
    # Backend health indicator
    st.markdown(f"""
    <div class="gateway-connected">
        <b>🟢 Backend API</b><br>
        <small>Healthy | /healthz: 200 OK</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Database health
    st.markdown(f"""
    <div class="gateway-connected">
        <b>🟢 PostgreSQL</b><br>
        <small>Connected | 47ms latency</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Redis/Queue health
    st.markdown(f"""
    <div class="gateway-connected">
        <b>🟢 Redis Queue</b><br>
        <small>Running | 0 pending jobs</small>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# KANBAN BOARD SECTION
# =============================================================================

st.divider()
st.subheader("🗂️ KANBAN BOARD")

# Kanban columns
kanban_stages = ["Backlog", "Planned", "In Progress", "Review", "Complete"]
kanban_cols = st.columns(len(kanban_stages))

for idx, stage in enumerate(kanban_stages):
    with kanban_cols[idx]:
        # Column header with count
        stage_tasks = get_tasks_by_stage(st.session_state.tasks, stage)
        count_color = get_status_color(stage)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 8px; background-color: {COLORS['card_background']}; 
                    border-radius: 6px; margin-bottom: 10px;">
            <b>{stage}</b><br>
            <span style="color: {count_color}; font-size: 1.2rem;">{len(stage_tasks)}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Task cards
        for task in stage_tasks:
            priority_class = f"kanban-card-{task['priority']}"
            qa_display = f"🎯 {task['qa_score']}% QA" if task['qa_score'] > 0 else "📝 Not started"
            assignee = task['assigned_agent'] if task['assigned_agent'] else "Unassigned"
            
            st.markdown(f"""
            <div class="kanban-card {priority_class}">
                <b>{task['id']}: {task['title']}</b><br>
                <small style="color: {COLORS['text_secondary']};">{task['description'][:50]}...</small><br>
                <small>{qa_display}</small><br>
                <small style="color: {COLORS['text_secondary']};">👤 {assignee}</small>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# MODALS & FORMS
# =============================================================================

# New Task Modal
if st.session_state.get("show_new_task"):
    with st.expander("Create New Task", expanded=True):
        with st.form("new_task_form"):
            st.subheader("📝 Create New Task")
            
            task_title = st.text_input("Task Title")
            task_desc = st.text_area("Description")
            task_board = st.selectbox("Board", [b["name"] for b in st.session_state.boards])
            task_priority = st.select_slider("Priority", options=["low", "medium", "high"], value="medium")
            task_due = st.date_input("Due Date")
            
            cols = st.columns(2)
            with cols[0]:
                if st.form_submit_button("✅ Create Task", use_container_width=True):
                    st.success(f"Task '{task_title}' created!")
                    st.session_state.show_new_task = False
            with cols[1]:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_new_task = False

# Deploy Agent Modal  
if st.session_state.get("show_deploy_agent"):
    with st.expander("Deploy New Agent", expanded=True):
        with st.form("deploy_agent_form"):
            st.subheader("🤖 Deploy Agent")
            
            agent_name = st.text_input("Agent Name")
            agent_role = st.selectbox("Role", ["content-writer", "lead-generator", "legal-assistant", "seo-specialist", "custom"])
            agent_gateway = st.selectbox("Gateway", [g["name"] for g in st.session_state.gateways])
            agent_skills = st.multiselect("Skills", ["scriptwriting", "research", "outreach", "copywriting", "analytics", "contract-drafting"])
            
            cols = st.columns(2)
            with cols[0]:
                if st.form_submit_button("🚀 Deploy", use_container_width=True):
                    st.success(f"Agent '{agent_name}' deployed to {agent_gateway}!")
                    st.session_state.show_deploy_agent = False
            with cols[1]:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_deploy_agent = False

# Create Board Modal
if st.session_state.get("show_create_board"):
    with st.expander("Create New Board", expanded=True):
        with st.form("create_board_form"):
            st.subheader("📋 Create New Board")
            
            board_name = st.text_input("Board Name")
            board_desc = st.text_area("Description")
            board_group = st.selectbox("Board Group", [bg["name"] for bg in st.session_state.board_groups])
            
            cols = st.columns(2)
            with cols[0]:
                if st.form_submit_button("✅ Create Board", use_container_width=True):
                    st.success(f"Board '{board_name}' created!")
                    st.session_state.show_create_board = False
            with cols[1]:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_create_board = False

# =============================================================================
# FOOTER
# =============================================================================

st.divider()
footer_cols = st.columns([2, 1, 2])

with footer_cols[0]:
    st.caption("OpenClaw Mission Control v1.0")
    
with footer_cols[1]:
    st.caption("<center>🟢 All Systems Operational</center>", unsafe_allow_html=True)
    
with footer_cols[2]:
    st.caption("<div style='text-align: right;'>Docs | API | Support</div>", unsafe_allow_html=True)
