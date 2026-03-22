"""
Live Data Manager for Cricbuzz LiveStats

Manages real-time data refresh for live matches and database synchronization.
Provides utility functions for auto-refresh and data synchronization.
"""

import streamlit as st
from datetime import datetime, timedelta
import time

class LiveDataManager:
    """Manage live data refresh intervals and updates."""
    
    @staticmethod
    def init_session_state():
        """Initialize session state for live updates."""
        if 'live_data_last_sync' not in st.session_state:
            st.session_state.live_data_last_sync = datetime.now()
        
        if 'live_data_auto_refresh' not in st.session_state:
            st.session_state.live_data_auto_refresh = True
        
        if 'live_data_refresh_interval' not in st.session_state:
            st.session_state.live_data_refresh_interval = 5  # seconds
    
    @staticmethod
    def get_time_since_sync():
        """Get seconds since last sync."""
        return (datetime.now() - st.session_state.live_data_last_sync).total_seconds()
    
    @staticmethod
    def should_refresh():
        """Check if refresh is needed based on interval."""
        return LiveDataManager.get_time_since_sync() >= st.session_state.live_data_refresh_interval
    
    @staticmethod
    def update_sync_time():
        """Update last sync timestamp."""
        st.session_state.live_data_last_sync = datetime.now()
    
    @staticmethod
    def display_refresh_status():
        """Display refresh status metrics."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            auto_status = "🟢 Enabled" if st.session_state.live_data_auto_refresh else "🔴 Disabled"
            st.metric("Auto Refresh", auto_status)
        
        with col2:
            st.metric("Refresh Interval", f"{st.session_state.live_data_refresh_interval}s")
        
        with col3:
            time_since = LiveDataManager.get_time_since_sync()
            if time_since < 60:
                status = f"{int(time_since)}s ago"
            else:
                status = f"{int(time_since/60)}m ago"
            st.metric("Last Updated", status)
    
    @staticmethod
    def display_refresh_controls():
        """Display refresh control buttons and settings."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.live_data_auto_refresh = st.checkbox(
                "🔄 Auto Refresh",
                value=st.session_state.live_data_auto_refresh,
                help="Automatically refresh live data"
            )
        
        with col2:
            st.session_state.live_data_refresh_interval = st.slider(
                "Interval (sec)",
                min_value=2,
                max_value=60,
                value=st.session_state.live_data_refresh_interval,
                step=1,
                help="Time between refreshes"
            )
        
        with col3:
            if st.button("🔄 Refresh Now"):
                LiveDataManager.update_sync_time()
                st.rerun()
    
    @staticmethod
    def auto_refresh_placeholder():
        """
        Create placeholder for auto-refresh.
        Call this at the bottom of pages for auto-refresh support.
        """
        # This creates a placeholder that can trigger reruns
        if st.session_state.live_data_auto_refresh and LiveDataManager.should_refresh():
            LiveDataManager.update_sync_time()
            st.rerun()
        elif st.session_state.live_data_auto_refresh:
            # Show countdown to next refresh
            time_remaining = st.session_state.live_data_refresh_interval - LiveDataManager.get_time_since_sync()
            st.caption(f"Next update in {max(0, int(time_remaining))}s... 🔄")


class LiveMatchesRefresh:
    """Specialized refresh manager for live matches."""
    
    @staticmethod
    def display_live_refresh_header():
        """Display refresh controls for live matches page."""
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.session_state.live_matches_auto_refresh = st.checkbox(
                "🔄 Auto Refresh",
                value=getattr(st.session_state, 'live_matches_auto_refresh', True),
                key="live_refresh_checkbox"
            )
        
        with col2:
            interval = st.slider(
                "Refresh Every",
                min_value=1,
                max_value=30,
                value=getattr(st.session_state, 'live_matches_refresh_interval', 5),
                step=1,
                key="live_refresh_slider"
            )
            st.session_state.live_matches_refresh_interval = interval
        
        with col3:
            if st.button("🔄 Refresh Now", key="live_refresh_now"):
                st.session_state.live_matches_manual_refresh = True
                st.rerun()
        
        with col4:
            # Display time since last update
            last_update = getattr(st.session_state, 'live_matches_last_update', datetime.now())
            time_diff = (datetime.now() - last_update).total_seconds()
            if time_diff < 60:
                st.metric("Last Update", f"{int(time_diff)}s ago")
            else:
                st.metric("Last Update", f"{int(time_diff/60)}m ago")
        
        st.markdown("---")
