import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Box,
    Card,
    CardContent,
    Grid,
    Typography,
    Alert,
    Chip,
    Divider,
    CircularProgress,
    IconButton,
    Tooltip,
    TextField,
    Button
} from '@mui/material';
import {
    PowerSettingsNew,
    Settings,
    CheckCircle,
    Warning,
    Email,
    Refresh,
    Info,
    NotificationsActive,
    Assessment
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { API_ENDPOINTS } from '../constants.js';

const SystemControls = ({ darkMode, themeColor, themeColors }) => {
    const [systemHealth, setSystemHealth] = useState(null);
    const [isLoadingHealth, setIsLoadingHealth] = useState(true);
    const [lastHealthUpdate, setLastHealthUpdate] = useState(null);
    
    const [systemSettings, setSystemSettings] = useState(null);
    const [isLoadingSettings, setIsLoadingSettings] = useState(true);
    
    const [notificationStatus, setNotificationStatus] = useState(null);
    const [notificationEmail, setNotificationEmail] = useState('');
    const [isSavingEmail, setIsSavingEmail] = useState(false);
    
    const currentTheme = themeColors[themeColor];

    useEffect(() => {
        fetchSystemHealth();
        fetchSystemSettings();
        fetchNotificationStatus();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchSystemHealth = async (forceRefresh = false) => {
        try {
            const url = forceRefresh 
                ? `${API_ENDPOINTS.systemHealth()}?force_refresh=true`
                : API_ENDPOINTS.systemHealth();
            const response = await axios.get(url);
            const newHealthData = response.data;
            
            setSystemHealth(newHealthData);
            setLastHealthUpdate(new Date());
            setIsLoadingHealth(false);
        } catch (error) {
            console.error('Error fetching system health:', error);
            setIsLoadingHealth(false);
        }
    };

    const fetchSystemSettings = async (forceRefresh = false) => {
        try {
            const url = forceRefresh 
                ? `${API_ENDPOINTS.systemSettings()}?force_refresh=true`
                : API_ENDPOINTS.systemSettings();
            const response = await axios.get(url);
            if (response.data.success) {
                const newSettings = response.data.settings;
                
                if (systemSettings) {
                    if (systemSettings.grid_feed_enabled !== newSettings.grid_feed_enabled) {
                        toast.info(`⚡ Grid Feeding ${newSettings.grid_feed_enabled ? 'ENABLED' : 'DISABLED'}`);
                    }
                    if (systemSettings.output_source_priority !== newSettings.output_source_priority) {
                        toast.info(`🔄 Output Priority changed to: ${newSettings.output_source_priority}`);
                    }
                }
                
                setSystemSettings(newSettings);
            }
            setIsLoadingSettings(false);
        } catch (error) {
            console.error('Error fetching system settings:', error);
            setIsLoadingSettings(false);
        }
    };

    const fetchNotificationStatus = async () => {
        try {
            const response = await axios.get(API_ENDPOINTS.notificationStatus());
            if (response.data.success) {
                setNotificationStatus(response.data);
                setNotificationEmail(response.data.notification_email || '');
            }
        } catch (error) {
            console.error('Error fetching notification status:', error);
        }
    };

    const handleTestNotification = async () => {
        try {
            console.log('🔔 Sending test notification...');
            const response = await axios.post(API_ENDPOINTS.notificationTest());
            console.log('📧 Test notification response:', response.data);
            
            if (response.data && response.data.success) {
                const recipient = response.data.recipient || 'configured email';
                toast.success(`✅ Test email sent to ${recipient}`);
            } else {
                const errorMessage = response.data?.message || 'Failed to send test email';
                console.error('❌ Test notification failed:', errorMessage);
                toast.error(errorMessage);
            }
        } catch (error) {
            console.error('❌ Test notification error:', error);
            
            // Handle different types of errors
            if (error.response) {
                // Server responded with error status
                const errorMessage = error.response.data?.message || error.response.data?.error || `Server error: ${error.response.status}`;
                toast.error(`Error sending test email: ${errorMessage}`);
            } else if (error.request) {
                // Request was made but no response received
                toast.error('Network error: Unable to reach server');
            } else {
                // Something else happened
                toast.error(`Error: ${error.message}`);
            }
        }
    };

    const handleTestDailySummary = async () => {
        try {
            toast.info('Fetching yesterday\'s data and sending summary...', { autoClose: 2000 });
            
            const response = await axios.post(API_ENDPOINTS.testDailySummary());
            
            if (response.data.success) {
                toast.success(response.data.message || 'Daily summary email sent!');
            } else {
                toast.error(response.data.message || 'Failed to send daily summary');
            }
        } catch (error) {
            toast.error('Error sending daily summary: ' + error.message);
        }
    };

    const handleSaveNotificationEmail = async () => {
        if (!notificationEmail) {
            toast.error('Please enter an email address');
            return;
        }
        try {
            setIsSavingEmail(true);
            await axios.put(API_ENDPOINTS.notificationEmail(), {
                notification_email: notificationEmail
            });
            toast.success('Notification email updated');
            fetchNotificationStatus();
        } catch (error) {
            const message =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                'Unable to update email';
            toast.error(message);
        } finally {
            setIsSavingEmail(false);
        }
    };

    const handleRefresh = () => {
        setIsLoadingHealth(true);
        setIsLoadingSettings(true);
        toast.info('Fetching fresh data from inverter...');
        fetchSystemHealth(true);
        fetchSystemSettings(true);
        fetchNotificationStatus();
    };

    const getHealthColor = (score) => {
        if (score >= 90) return '#4caf50';
        if (score >= 70) return '#ff9800';
        return '#f44336';
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Online': return 'success';
            case 'Warning': return 'warning';
            case 'Critical': return 'error';
            default: return 'default';
        }
    };

    const getStatusChipColor = (enabled) => {
        return enabled ? 'success' : 'error';
    };

    return (
        <Box>
            <Box sx={{ 
                mb: 3, 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                flexDirection: { xs: 'column', sm: 'row' },
                gap: 2
            }}>
                <Box sx={{ textAlign: { xs: 'center', sm: 'left' }, width: { xs: '100%', sm: 'auto' } }}>
                    <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, fontSize: { xs: '1.75rem', sm: '2.125rem' } }}>
                        System Status & Monitoring
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.7, fontSize: { xs: '0.875rem', sm: '0.875rem' } }}>
                        Real-time system settings and health monitoring (READ-ONLY)
                    </Typography>
                </Box>
                <Tooltip title="Refresh All Data">
                    <IconButton 
                        onClick={handleRefresh}
                        sx={{
                            background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                            color: 'white',
                            '&:hover': {
                                background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                transform: 'rotate(180deg)',
                            },
                            transition: 'all 0.5s ease',
                        }}
                    >
                        <Refresh />
                    </IconButton>
                </Tooltip>
            </Box>

            <Alert severity="info" sx={{ mb: 2 }}>
                <strong>📖 Read-Only Display:</strong> These settings are read directly from your inverter hardware. 
                To change them, use the WatchPower mobile app. This dashboard monitors values and sends email alerts.
            </Alert>
            
            <Alert severity="success" sx={{ mb: 3 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    🤖 Automatic Monitoring Active - Every 5 Minutes
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                    The system automatically checks for mode changes and sends instant alerts via Email 📧, Telegram 📱, and Discord 💬 when:
                    <br />• Electricity disconnects (Battery Mode) 🔋
                    <br />• Electricity restores (Line Mode) ⚡
                    <br />• System goes to Standby ⏸️
                </Typography>
            </Alert>

            <Grid container spacing={{ xs: 2, sm: 3 }}>
                <Grid item xs={12} md={6}>
                    <Card
                        sx={{
                            background: darkMode 
                                ? 'linear-gradient(145deg, #1e1e1e 0%, #2d2d2d 100%)'
                                : 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                            borderRadius: 4,
                            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                            border: `1px solid ${darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'}`,
                            height: '100%'
                        }}
                    >
                        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                                <Settings sx={{ fontSize: { xs: 28, sm: 32 }, mr: 2, color: currentTheme.primary }} />
                                <Typography variant="h5" sx={{ fontWeight: 600, fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
                                    System Health
                                </Typography>
                            </Box>

                            {isLoadingHealth ? (
                                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                                    <CircularProgress />
                                </Box>
                            ) : systemHealth ? (
                                <>
                                    <Box sx={{ 
                                        textAlign: 'center', 
                                        mb: 3,
                                        p: { xs: 2, sm: 3 },
                                        background: systemHealth.system_mode === 'Battery Mode'
                                            ? 'linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%)'
                                            : systemHealth.system_mode === 'Standby Mode'
                                                ? 'linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 193, 7, 0.15) 100%)'
                                                : `linear-gradient(135deg, ${currentTheme.primary}15 0%, ${currentTheme.secondary}15 100%)`,
                                        borderRadius: 3,
                                        border: systemHealth.system_mode === 'Battery Mode'
                                            ? '2px solid rgba(244, 67, 54, 0.3)'
                                            : systemHealth.system_mode === 'Standby Mode'
                                                ? '2px solid rgba(255, 152, 0, 0.3)'
                                                : 'none'
                                    }}>
                                        <Typography variant="h1" sx={{ 
                                            fontWeight: 700,
                                            color: getHealthColor(systemHealth.health_score),
                                            mb: 1,
                                            fontSize: { xs: '3rem', sm: '4rem', md: '6rem' }
                                        }}>
                                            {systemHealth.health_score}
                                        </Typography>
                                        <Typography variant="h6" sx={{ opacity: 0.7, mb: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                                            Health Score
                                        </Typography>
                                        <Chip 
                                            label={systemHealth.status}
                                            color={getStatusColor(systemHealth.status)}
                                            sx={{ fontWeight: 600 }}
                                        />
                                    </Box>

                                    {systemHealth.system_mode === 'Battery Mode' && (
                                        <Alert severity="warning" sx={{ mb: 2 }}>
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                🔋 Electricity Disconnected - Running on Battery Power
                                            </Typography>
                                        </Alert>
                                    )}
                                    {systemHealth.system_mode === 'Standby Mode' && (
                                        <Alert severity="error" sx={{ mb: 2 }}>
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                ⏸️ System in Standby Mode - Power Off
                                            </Typography>
                                        </Alert>
                                    )}
                                    {systemHealth.system_mode === 'Line Mode' && (
                                        <Alert severity="success" sx={{ mb: 2 }}>
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                ⚡ Electricity Connected - Grid Power Active
                                            </Typography>
                                        </Alert>
                                    )}

                                    <Divider sx={{ my: 2 }} />

                                    <Grid container spacing={{ xs: 1.5, sm: 2 }}>
                                        <Grid item xs={6} sm={6}>
                                            <Box sx={{ 
                                                p: { xs: 1.5, sm: 2 }, 
                                                background: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)', 
                                                borderRadius: 2 
                                            }}>
                                                <Typography variant="body2" sx={{ opacity: 0.7, mb: 0.5, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                                                    Grid Voltage
                                                </Typography>
                                                <Typography variant="h6" sx={{ 
                                                    fontWeight: 600, 
                                                    fontSize: { xs: '1rem', sm: '1.25rem' },
                                                    color: (systemHealth.utility_ac_voltage === 0 || systemHealth.utility_ac_voltage === null) ? '#f44336' : 'inherit'
                                                }}>
                                                    {(systemHealth.utility_ac_voltage === 0 || systemHealth.utility_ac_voltage === null) ? 'Not Available' : `${systemHealth.utility_ac_voltage}V`}
                                                </Typography>
                                            </Box>
                                        </Grid>
                                        <Grid item xs={6} sm={6}>
                                            <Box sx={{ 
                                                p: { xs: 1.5, sm: 2 }, 
                                                background: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)', 
                                                borderRadius: 2 
                                            }}>
                                                <Typography variant="body2" sx={{ opacity: 0.7, mb: 0.5, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                                                    PV Power
                                                </Typography>
                                                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                                                    {systemHealth.pv_charging_power}W
                                                </Typography>
                                            </Box>
                                        </Grid>
                                        <Grid item xs={6} sm={6}>
                                            <Box sx={{ 
                                                p: { xs: 1.5, sm: 2 }, 
                                                background: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)', 
                                                borderRadius: 2 
                                            }}>
                                                <Typography variant="body2" sx={{ opacity: 0.7, mb: 0.5, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                                                    Load Power
                                                </Typography>
                                                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                                                    {systemHealth.ac_output_power}W
                                                </Typography>
                                            </Box>
                                        </Grid>
                                        <Grid item xs={6} sm={6}>
                                            <Box sx={{ 
                                                p: { xs: 1.5, sm: 2 }, 
                                                background: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)', 
                                                borderRadius: 2 
                                            }}>
                                                <Typography variant="body2" sx={{ opacity: 0.7, mb: 0.5, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                                                    Load %
                                                </Typography>
                                                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                                                    {systemHealth.output_load_percent}%
                                                </Typography>
                                            </Box>
                                        </Grid>
                                    </Grid>

                                    {/* Warnings & Errors */}
                                    {systemHealth.warnings && systemHealth.warnings.length > 0 && (
                                        <Box sx={{ mt: 2 }}>
                                            {systemHealth.warnings.map((warning, index) => (
                                                <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                                                    {warning}
                                                </Alert>
                                            ))}
                                        </Box>
                                    )}
                                    {systemHealth.errors && systemHealth.errors.length > 0 && (
                                        <Box sx={{ mt: 2 }}>
                                            {systemHealth.errors.map((error, index) => (
                                                <Alert key={index} severity="error" sx={{ mb: 1 }}>
                                                    {error}
                                                </Alert>
                                            ))}
                                        </Box>
                                    )}

                                    <Box sx={{ 
                                        mt: 2, 
                                        p: 2, 
                                        background: systemHealth.system_mode === 'Battery Mode' 
                                            ? 'rgba(244, 67, 54, 0.1)' 
                                            : systemHealth.system_mode === 'Line Mode'
                                                ? 'rgba(76, 175, 80, 0.1)'
                                                : 'rgba(255, 152, 0, 0.1)',
                                        borderRadius: 2,
                                        border: systemHealth.system_mode === 'Battery Mode'
                                            ? '1px solid rgba(244, 67, 54, 0.3)'
                                            : systemHealth.system_mode === 'Line Mode'
                                                ? '1px solid rgba(76, 175, 80, 0.3)'
                                                : '1px solid rgba(255, 152, 0, 0.3)'
                                    }}>
                                        <Typography variant="body2" sx={{ opacity: 0.8, mb: 0.5 }}>
                                            System Mode: <strong style={{ 
                                                color: systemHealth.system_mode === 'Battery Mode' 
                                                    ? '#f44336' 
                                                    : systemHealth.system_mode === 'Line Mode'
                                                        ? '#4caf50'
                                                        : '#ff9800'
                                            }}>{systemHealth.system_mode}</strong>
                                        </Typography>
                                        <Typography variant="caption" sx={{ opacity: 0.6, display: 'block' }}>
                                            {systemHealth.system_mode === 'Line Mode' && '⚡ Connected to Grid'}
                                            {systemHealth.system_mode === 'Battery Mode' && '🔋 Running on Battery'}
                                            {systemHealth.system_mode === 'Standby Mode' && '⏸️ System Off'}
                                        </Typography>
                                        <Typography variant="caption" sx={{ opacity: 0.5, display: 'block', mt: 1 }}>
                                            Last updated: {new Date(systemHealth.timestamp).toLocaleTimeString()}
                                        </Typography>
                                        {lastHealthUpdate && (
                                            <Typography variant="caption" sx={{ opacity: 0.5, display: 'block' }}>
                                                Checked: {Math.floor((new Date() - lastHealthUpdate) / 1000)}s ago
                                            </Typography>
                                        )}
                                    </Box>
                                </>
                            ) : (
                                <Alert severity="error">Failed to load system health</Alert>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Grid container spacing={{ xs: 2, sm: 3 }}>
                        <Grid item xs={12}>
                            <Card
                                sx={{
                                    background: `linear-gradient(135deg, ${currentTheme.primary}20 0%, ${currentTheme.secondary}20 100%)`,
                                    borderRadius: 4,
                                    border: `2px solid ${currentTheme.primary}40`
                                }}
                            >
                                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                        <PowerSettingsNew sx={{ fontSize: { xs: 28, sm: 32 }, mr: 2, color: currentTheme.primary }} />
                                        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: { xs: '1.1rem', sm: '1.25rem' } }}>
                                            Actual System Settings
                                        </Typography>
                                    </Box>

                                    {isLoadingSettings ? (
                                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                            <CircularProgress size={32} />
                                        </Box>
                                    ) : systemSettings ? (
                                        <>
                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ opacity: 0.8, mb: 1, fontWeight: 600, fontSize: { xs: '0.875rem', sm: '0.875rem' } }}>
                                                    🔌 Grid Feeding:
                                                </Typography>
                                                <Chip 
                                                    icon={systemSettings.grid_feed_enabled ? <CheckCircle /> : <Warning />}
                                                    label={systemSettings.grid_feed_display || (systemSettings.grid_feed_enabled ? 'ENABLED' : 'DISABLED')}
                                                    color={getStatusChipColor(systemSettings.grid_feed_enabled)}
                                                    sx={{ 
                                                        fontWeight: 600, 
                                                        fontSize: { xs: '0.75rem', sm: '0.875rem' }, 
                                                        px: { xs: 1.5, sm: 2 }, 
                                                        py: { xs: 2, sm: 2.5 },
                                                        height: 'auto'
                                                    }}
                                                />
                                                {systemSettings.solar_feed_power !== undefined && (
                                                    <Box sx={{ mt: 1 }}>
                                                        <Typography variant="caption" sx={{ opacity: 0.7 }}>
                                                            Current Feed: <strong>{systemSettings.solar_feed_power}W</strong>
                                                            {systemSettings.pv_power !== undefined && (
                                                                <span> | PV Production: <strong>{systemSettings.pv_power}W</strong></span>
                                                            )}
                                                        </Typography>
                                                    </Box>
                                                )}
                                            </Box>

                                            <Divider sx={{ my: 2 }} />

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                                                    <strong>Load Status:</strong> {systemSettings.load_status}
                                                </Typography>
                                            </Box>

                                            <Divider sx={{ my: 2 }} />

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                                                    <strong>Output Priority:</strong> {systemSettings.output_source_priority}
                                                </Typography>
                                            </Box>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                                                    <strong>Charger Priority:</strong> {systemSettings.charger_source_priority}
                                                </Typography>
                                            </Box>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                                                    <strong>AC Input Range:</strong> {systemSettings.ac_input_range}
                                                </Typography>
                                            </Box>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                                                    <strong>System Status:</strong> {systemSettings.system_status}
                                                </Typography>
                                            </Box>

                                            {!systemSettings.grid_feed_enabled && (
                                                <Alert severity="warning" sx={{ mt: 2 }}>
                                                    ⚠️ Grid feeding is disabled. You'll receive email reminders every 6 hours.
                                                </Alert>
                                            )}

                                            <Alert severity="info" icon={<Info />} sx={{ mt: 2 }}>
                                                Use WatchPower app to change these settings
                                            </Alert>
                                        </>
                                    ) : (
                                        <Alert severity="error">Failed to load settings</Alert>
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12}>
                            <Card 
                                sx={{ 
                                    borderRadius: 4,
                                    background: notificationStatus?.email_configured 
                                        ? 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)'
                                        : 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)'
                                }}
                            >
                                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                        <Email sx={{ fontSize: { xs: 24, sm: 28 }, mr: 2, color: currentTheme.primary }} />
                                        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: { xs: '1.1rem', sm: '1.25rem' } }}>
                                            Email Notifications
                                        </Typography>
                                    </Box>
                                    {notificationStatus ? (
                                        <>
                                            <Box sx={{ mb: 2 }}>
                                                <Chip
                                                icon={notificationStatus.email_configured ? <CheckCircle /> : <Warning />}
                                                label={notificationStatus.email_configured ? 'Configured' : 'Not Configured'}
                                                color={notificationStatus.email_configured ? 'success' : 'error'}
                                                    sx={{ mb: 1 }}
                                                />
                                            <Typography variant="body2" sx={{ opacity: 0.8 }}>
                                                {notificationStatus.notification_email
                                                    ? `📧 ${notificationStatus.notification_email}`
                                                    : 'Add an email address to receive alerts.'}
                                            </Typography>
                                        </Box>

                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 2 }}>
                                            <TextField
                                                label="Notification Email"
                                                type="email"
                                                value={notificationEmail}
                                                onChange={(e) => setNotificationEmail(e.target.value)}
                                                fullWidth
                                            />
                                            <Button
                                                variant="contained"
                                                onClick={handleSaveNotificationEmail}
                                                disabled={isSavingEmail}
                                                sx={{ textTransform: 'none', fontWeight: 600 }}
                                            >
                                                {isSavingEmail ? 'Saving...' : 'Save Email'}
                                            </Button>
                                            </Box>
                                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                                <IconButton
                                                    onClick={handleTestNotification}
                                                    sx={{
                                                        background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                                        color: 'white',
                                                        borderRadius: 2,
                                                        py: 1,
                                                        '&:hover': {
                                                            background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                                        }
                                                    }}
                                                >
                                                    <NotificationsActive sx={{ mr: 1 }} />
                                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                        Send Test Email
                                                    </Typography>
                                                </IconButton>
                                                
                                                <IconButton
                                                    onClick={handleTestDailySummary}
                                                    sx={{
                                                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                        color: 'white',
                                                        borderRadius: 2,
                                                        py: 1,
                                                        '&:hover': {
                                                            background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                                                        }
                                                    }}
                                                >
                                                    <Assessment sx={{ mr: 1 }} />
                                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                        Test Daily Summary
                                                    </Typography>
                                                </IconButton>
                                            </Box>
                                        </>
                                    ) : (
                                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                            <CircularProgress size={32} />
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Box>
    );
};

export default SystemControls;