'use client';

import { useEffect, useState } from "react";
import axios from "axios";
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    Legend,
    ReferenceArea
} from "recharts";
import {
    Box,
    Card,
    CardContent,
    Grid,
    Paper,
    InputAdornment,
    TextField,
    Fade,
    Chip,
    Tooltip,
    IconButton,
    Button,
    Typography,
    Alert,
    useTheme as useMuiTheme
} from "@mui/material";
import {
    SolarPower as SolarIcon,
    CalendarToday,
    Refresh,
    TrendingUp,
    BatteryChargingFull,
    PowerOff,
    ChevronLeft,
    ChevronRight,
    Fullscreen,
    FullscreenExit,
    PlayArrow,
    Pause,
    Today as TodayIcon
} from "@mui/icons-material";
import { toast } from "react-toastify";
import { API_ENDPOINTS, CONFIG } from "@/lib/constants";
import { themeColors } from "@/components/DashboardLayout";

export default function DailyStatsPage() {
    const muiTheme = useMuiTheme();
    const darkMode = muiTheme.palette.mode === 'dark';
    const themeColor = 'purple';
    
    const [data, setData] = useState<any[]>([]);
    const [total, setTotal] = useState(0);
    const [loadTotal, setLoadTotal] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [modeZones, setModeZones] = useState<any[]>([]);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [loadSheddingHours, setLoadSheddingHours] = useState(0);
    const [cutOffHours, setcutOffHours] = useState(0);
    const [missingDataHours, setMissingDataHours] = useState(0);
    const [expectedDataPoints, setExpectedDataPoints] = useState(CONFIG.EXPECTED_DATA_POINTS_PER_DAY);
    const [missingDataGaps, setMissingDataGaps] = useState<any[]>([]);
    const [isLiveMode, setIsLiveMode] = useState(true);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isError, setisError] = useState("");
    const [gridFeedEnabled, setGridFeedEnabled] = useState<boolean | null>(null);
    const [isLoadingGridStatus, setIsLoadingGridStatus] = useState(true);

    const getTodayLocal = () => {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    };

    const [selectedDate, setSelectedDate] = useState(getTodayLocal());

    const getModeColor = (mode: string) => {
        return mode === "Line Mode"
            ? "rgba(76, 175, 80, 0.2)"
            : mode === "Battery Mode"
                ? "rgba(244, 67, 54, 0.2)"
                : mode === "Standby Mode"
                    ? "rgba(255, 152, 0, 0.2)"
                    : "rgba(158, 158, 158, 0.2)";
    };

    const processModeZones = (graphData: any[]) => {
        const zones: any[] = [];
        let currentMode: string | null = null;
        let startIndex = 0;

        graphData.forEach((point, index) => {
            if (point.mode !== currentMode) {
                if (currentMode !== null) {
                    zones.push({
                        start: startIndex,
                        end: index - 1,
                        mode: currentMode
                    });
                }
                currentMode = point.mode;
                startIndex = index;
            }
        });

        if (currentMode !== null) {
            zones.push({
                start: startIndex,
                end: graphData.length - 1,
                mode: currentMode
            });
        }

        return zones;
    };

    const fetchData = async (date: string) => {
        try {
            const res = await axios.get(API_ENDPOINTS.getDailyStats(date));
            
            if (res.data.success) {
                const graphData = res.data.graph;

                let pvSum = 0;
                let loadSum = 0;
                const intervalHours = CONFIG.DATA_INTERVAL_MINUTES / 60;

                let batteryHours = 0;
                let cutOffHours = 0;

                graphData.forEach((point: any) => {
                    pvSum += point.pv_power * intervalHours;
                    loadSum += point.load_power * intervalHours;

                    if (point.mode === "Battery Mode") {
                        batteryHours += intervalHours;
                    }
                    if (point.mode === "Standby Mode") {
                        cutOffHours += intervalHours;
                    }
                });

                // Calculate missing data
                const today = getTodayLocal();
                const isToday = date === today;
                
                let expectedDataPoints;
                if (isToday) {
                    const now = new Date();
                    const minutesSinceMidnight = now.getHours() * 60 + now.getMinutes();
                    expectedDataPoints = Math.floor(minutesSinceMidnight / CONFIG.DATA_INTERVAL_MINUTES);
                } else {
                    expectedDataPoints = CONFIG.EXPECTED_DATA_POINTS_PER_DAY;
                }
                
                const actualDataPoints = graphData.length;
                const missingDataPoints = Math.max(0, expectedDataPoints - actualDataPoints);
                const missingHours = (missingDataPoints * CONFIG.DATA_INTERVAL_MINUTES) / 60;

                // Calculate missing data gaps
                const gaps = [];
                if (graphData.length > 1) {
                    for (let i = 1; i < graphData.length; i++) {
                        const prevTime = graphData[i - 1].time;
                        const currTime = graphData[i].time;
                        
                        const [prevHour, prevMin] = prevTime.split(':').map(Number);
                        const [currHour, currMin] = currTime.split(':').map(Number);
                        
                        const prevMinutes = prevHour * 60 + prevMin;
                        const currMinutes = currHour * 60 + currMin;
                        const timeDiff = currMinutes - prevMinutes;
                        
                        if (timeDiff > 6) {
                            gaps.push({
                                start: prevTime,
                                end: currTime,
                                duration: timeDiff - 5
                            });
                        }
                    }
                }

                setData(graphData);
                setTotal(Number((pvSum / 1000).toFixed(2)));
                setLoadTotal(Number((loadSum / 1000).toFixed(2)));
                setModeZones(processModeZones(graphData));
                setLastUpdated(new Date());
                setMissingDataGaps(gaps);
                setLoadSheddingHours(Number(batteryHours.toFixed(2)));
                setcutOffHours(Number(cutOffHours.toFixed(2)));
                setMissingDataHours(Number(missingHours.toFixed(2)));
                setExpectedDataPoints(expectedDataPoints);

            } else {
                setisError(res.data.error?.err || 'Unknown error');
                toast.error("Error fetching API");
                setData([]);
                setTotal(0);
                setLoadTotal(0);
                setModeZones([]);
                setMissingDataHours(0);
            }
        } catch (err: any) {
            toast.error("Error fetching API");
            setisError(err.message);
            console.error("Error fetching API:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchGridFeedStatus = async () => {
        try {
            const response = await axios.get(API_ENDPOINTS.systemSettings());
            if (response.data.success) {
                setGridFeedEnabled(response.data.settings?.grid_feed_enabled);
            }
            setIsLoadingGridStatus(false);
        } catch (error) {
            console.error('Error fetching grid feed status:', error);
            setIsLoadingGridStatus(false);
        }
    };

    useEffect(() => {
        const fetchAndSetLoading = async () => {
            setIsLoading(true);
            await fetchData(selectedDate);
        };
        fetchAndSetLoading();
        fetchGridFeedStatus();

        let interval: NodeJS.Timeout;
        if (isLiveMode) {
            interval = setInterval(() => {
                fetchData(selectedDate);
                fetchGridFeedStatus();
            }, CONFIG.AUTO_REFRESH_INTERVAL);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [selectedDate, isLiveMode]);

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const currentData = payload[0].payload;
            const modeColor = currentData.mode === "Line Mode"
                ? "#4caf50"
                : currentData.mode === "Battery Mode"
                    ? "#f44336"
                    : "#ff9800";

            return (
                <Paper 
                    elevation={12} 
                    sx={{ 
                        p: 2.5, 
                        backgroundColor: "rgba(255, 255, 255, 0.98)",
                        backdropFilter: 'blur(10px)',
                        borderRadius: 3,
                        border: '1px solid rgba(0, 0, 0, 0.1)',
                        minWidth: 200
                    }}
                >
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mb: 1.5, color: '#333' }}>
                        ⏰ {label}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Box sx={{ 
                            width: 12, 
                            height: 12, 
                            borderRadius: '50%', 
                            backgroundColor: '#82ca9d',
                            mr: 1.5
                        }} />
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            PV: <span style={{ color: '#82ca9d', fontWeight: 700 }}>{currentData.pv_power} W</span>
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        <Box sx={{ 
                            width: 12, 
                            height: 12, 
                            borderRadius: '50%', 
                            backgroundColor: '#8884d8',
                            mr: 1.5
                        }} />
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            Load: <span style={{ color: '#8884d8', fontWeight: 700 }}>{currentData.load_power} W</span>
                        </Typography>
                    </Box>
                    <Box sx={{ 
                        pt: 1.5, 
                        borderTop: '1px solid rgba(0, 0, 0, 0.1)',
                        display: 'flex',
                        alignItems: 'center'
                    }}>
                        <Box sx={{ 
                            width: 8, 
                            height: 8, 
                            borderRadius: '50%', 
                            backgroundColor: modeColor,
                            mr: 1.5
                        }} />
                        <Typography variant="body2" sx={{ color: modeColor, fontWeight: 700 }}>
                            {currentData.mode === "Line Mode" ? "⚡ Connected" :
                                currentData.mode === "Battery Mode" ? "🔋 Disconnected" :
                                    currentData.mode === "Standby Mode" ? "⏸️ System off" : "❓ Out of range"}
                        </Typography>
                    </Box>
                </Paper>
            );
        }
        return null;
    };

    const handleRefresh = () => {
        setIsLoading(true);
        setIsLoadingGridStatus(true);
        fetchData(selectedDate);
        fetchGridFeedStatus();
    };
    
    const handlePreviousDay = () => {
        const currentDate = new Date(selectedDate);
        currentDate.setDate(currentDate.getDate() - 1);
        const newDate = currentDate.toISOString().split('T')[0];
        setSelectedDate(newDate);
    };

    const handleNextDay = () => {
        const currentDate = new Date(selectedDate);
        const today = getTodayLocal();
        
        if (selectedDate < today) {
            currentDate.setDate(currentDate.getDate() + 1);
            const newDate = currentDate.toISOString().split('T')[0];
            setSelectedDate(newDate);
        }
    };
    
    const handleTodayClick = () => {
        setSelectedDate(getTodayLocal());
    };
    
    const handleFullscreenToggle = () => {
        setIsFullscreen(!isFullscreen);
    };
    
    const formatHours = (decimalHours: number) => {
        const hrs = Math.floor(decimalHours);
        const mins = Math.round((decimalHours - hrs) * 60);
        return `${hrs} hr ${mins} min`;
    };
    
    const formatMissingDuration = (minutes: number) => {
        if (minutes >= 60) {
            const hours = Math.floor(minutes / 60);
            const mins = Math.round(minutes % 60);
            if (mins === 0) {
                return `${hours} hr`;
            }
            return `${hours} hr ${mins} min`;
        }
        return `${Math.floor(minutes)} min`;
    };
    
    const currentTheme = themeColors[themeColor];

    return (
        <Box>
            <Grid container spacing={{ xs: 2, sm: 2, md: 3 }} sx={{ mb: { xs: 2, sm: 3 } }}>
                <Grid item xs={12} sm={6} md={6} lg={3} sx={{ display: 'flex' }}>
                    <Fade in timeout={500} style={{ width: '100%' }}>
                        <Card 
                            className="stat-card"
                            sx={{
                                width: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                color: "white",
                                borderRadius: 4,
                                boxShadow: "0 10px 40px rgba(102, 126, 234, 0.3)",
                                transition: "all 0.3s ease",
                                "&:hover": {
                                    transform: "translateY(-8px)",
                                    boxShadow: "0 15px 50px rgba(102, 126, 234, 0.4)",
                                }
                            }}
                        >
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ 
                                        opacity: 0.9, 
                                        textTransform: 'uppercase', 
                                        letterSpacing: 1,
                                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                                    }}>
                                Solar Production
                            </Typography>
                                    <SolarIcon sx={{ fontSize: { xs: 28, sm: 32 }, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ 
                                    fontWeight: 700, 
                                    mb: 1,
                                    fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
                                }}>
                                    {isLoading ? "..." : `${total}`}
                            </Typography>
                                <Typography variant="h6" sx={{ 
                                    opacity: 0.9,
                                    fontSize: { xs: '1rem', sm: '1.25rem' }
                                }}>
                                    kWh
                                </Typography>
                                <Typography variant="body2" sx={{ 
                                    opacity: 0.8, 
                                    mt: 1,
                                    fontSize: { xs: '0.75rem', sm: '0.875rem' }
                                }}>
                                Total PV Production
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
                <Grid item xs={12} sm={6} md={6} lg={3} sx={{ display: 'flex' }}>
                    <Fade in timeout={700} style={{ width: '100%' }}>
                        <Card 
                            className="stat-card"
                            sx={{
                                width: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                                color: "white",
                                borderRadius: 4,
                                boxShadow: "0 10px 40px rgba(240, 147, 251, 0.3)",
                                transition: "all 0.3s ease",
                                "&:hover": {
                                    transform: "translateY(-8px)",
                                    boxShadow: "0 15px 50px rgba(240, 147, 251, 0.4)",
                                }
                            }}
                        >
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
                                Energy Usage
                            </Typography>
                                    <TrendingUp sx={{ fontSize: 32, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                                    {isLoading ? "..." : `${loadTotal}`}
                            </Typography>
                                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                                    kWh
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
                                Total Load Consumption
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
                <Grid item xs={12} sm={6} md={6} lg={3} sx={{ display: 'flex' }}>
                    <Fade in timeout={900} style={{ width: '100%' }}>
                        <Card 
                            className="stat-card"
                            sx={{
                                width: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                                color: "white",
                                borderRadius: 4,
                                boxShadow: "0 10px 40px rgba(79, 172, 254, 0.3)",
                                transition: "all 0.3s ease",
                                "&:hover": {
                                    transform: "translateY(-8px)",
                                    boxShadow: "0 15px 50px rgba(79, 172, 254, 0.4)",
                                }
                            }}
                        >
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
                                        Grid Contribution
                            </Typography>
                                    <BatteryChargingFull sx={{ fontSize: 32, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                                    {isLoading ? "..." : `${(total - loadTotal).toFixed(2)}`}
                            </Typography>
                                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                                    kWh
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
                                    Energy Fed to Grid
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
                <Grid item xs={12} sm={6} md={6} lg={3} sx={{ display: 'flex' }}>
                    <Fade in timeout={1100} style={{ width: '100%' }}>
                        <Card 
                            className="stat-card"
                            sx={{
                                width: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                background: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
                                color: "white",
                                borderRadius: 4,
                                boxShadow: "0 10px 40px rgba(250, 112, 154, 0.3)",
                                transition: "all 0.3s ease",
                                "&:hover": {
                                    transform: "translateY(-8px)",
                                    boxShadow: "0 15px 50px rgba(250, 112, 154, 0.4)",
                                }
                            }}
                        >
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
                                        Load Shedding
                            </Typography>
                                    <PowerOff sx={{ fontSize: 32, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                                {isLoading ? "..." : formatHours(loadSheddingHours)}
                            </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
                                    Battery/Solar Runtime
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
                <Grid item xs={12} sm={12} md={6} sx={{ display: 'flex' }}>
                    <Fade in timeout={1300} style={{ width: '100%' }}>
                        <Card 
                            className="stat-card"
                            sx={{
                                width: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                background: "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
                                color: "#333",
                                borderRadius: 4,
                                boxShadow: "0 10px 40px rgba(168, 237, 234, 0.3)",
                                transition: "all 0.3s ease",
                                "&:hover": {
                                    transform: "translateY(-8px)",
                                    boxShadow: "0 15px 50px rgba(168, 237, 234, 0.4)",
                                }
                            }}
                        >
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1, fontWeight: 600 }}>
                                        System Off Duration
                                    </Typography>
                                    <PowerOff sx={{ fontSize: 32, opacity: 0.7 }} />
                                </Box>
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="h3" sx={{ fontWeight: 700, mb: 0.5 }}>
                                        {isLoading ? "..." : formatHours(parseFloat(cutOffHours.toString()) + parseFloat(missingDataHours.toString()))}
                                    </Typography>
                                    <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
                                        Total time system remained off
                                    </Typography>
                                </Box>
                                {!isLoading && (
                                    <Box sx={{ 
                                        mt: 2, 
                                        pt: 2, 
                                        borderTop: '2px solid rgba(0,0,0,0.1)',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        gap: 1
                                    }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Typography variant="body2" sx={{ opacity: 0.8, fontWeight: 500 }}>
                                                📊 Standby Mode:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 700 }}>
                                                {formatHours(cutOffHours)}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Typography variant="body2" sx={{ opacity: 0.8, fontWeight: 500 }}>
                                                ⚠️ Missing Data:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 700, color: missingDataHours > 0 ? '#f44336' : 'inherit' }}>
                                                {formatHours(missingDataHours)}
                                            </Typography>
                                        </Box>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    </Fade>
                </Grid>
            </Grid>
            {isError && (
                <Typography variant="body2" color="error" sx={{ mb: 2, p: 2, background: 'rgba(244, 67, 54, 0.1)', borderRadius: 2 }}>
                    ⚠️ Error: {isError}
                </Typography>
            )}
            {!isLoadingGridStatus && gridFeedEnabled === false && (
                <Alert 
                    severity="warning" 
                    sx={{ 
                        mb: 2, 
                        background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 87, 34, 0.1) 100%)',
                        border: '2px solid rgba(255, 152, 0, 0.3)',
                        borderRadius: 3
                    }}
                >
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ff5722', mb: 0.5 }}>
                        ⚠️ Grid Feeding Disabled
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>
                        Your system is not feeding excess power to the grid. Enable it in the WatchPower app to maximize ROI.
                    </Typography>
                </Alert>
            )}
            {!isLoading && missingDataHours > 0 && (
                <Card 
                    sx={{ 
                        mb: 2, 
                        background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 87, 34, 0.1) 100%)',
                        border: '2px solid rgba(255, 152, 0, 0.3)',
                        borderRadius: 3
                    }}
                >
                    <CardContent sx={{ py: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Box sx={{ 
                                background: 'linear-gradient(135deg, #ff9800 0%, #ff5722 100%)',
                                borderRadius: '50%',
                                p: 1.5,
                                display: 'flex'
                            }}>
                                <PowerOff sx={{ fontSize: 28, color: 'white' }} />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="h6" sx={{ fontWeight: 600, color: '#ff5722', mb: 0.5 }}>
                                    ⚠️ Missing API Data Detected
                                </Typography>
                                <Typography variant="body2" sx={{ color: '#666' }}>
                                    System was completely off for <strong>{formatHours(missingDataHours)}</strong> - No API responses received during this time. 
                                    Expected: {expectedDataPoints} data points (every 5 min) | Received: {data.length} data points | Missing: {Math.max(0, expectedDataPoints - data.length)} data points
                                </Typography>
                            </Box>
                        </Box>
                    </CardContent>
                </Card>
            )}
            <Card 
                className="muasn chart-card" 
                sx={{ 
                    mb: 3,
                    borderRadius: 4,
                    background: darkMode ? 'linear-gradient(145deg, #1e1e1e 0%, #2d2d2d 100%)' : 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                    border: `1px solid ${darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'}`,
                    ...(isFullscreen && {
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        zIndex: 9999,
                        m: 0,
                        borderRadius: 0,
                        height: '100vh',
                        overflow: 'auto'
                    })
                }}
            >
                <CardContent className="myasn" sx={{ p: { xs: 2, md: 4 }, height: isFullscreen ? '100%' : 'auto' }}>
                    {/* Control Bar */}
                    <Box sx={{ 
                        display: "flex", 
                        flexWrap: "wrap", 
                        gap: 2, 
                        alignItems: "center", 
                        mb: 3,
                        p: 2,
                        background: darkMode ? 'rgba(255,255,255,0.05)' : `linear-gradient(135deg, ${currentTheme.primary}15 0%, ${currentTheme.secondary}15 100%)`,
                        borderRadius: 3,
                        border: `1px solid ${darkMode ? 'rgba(255,255,255,0.1)' : `${currentTheme.primary}30`}`
                    }}>
                        <IconButton 
                            onClick={handlePreviousDay}
                            sx={{
                                background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                color: 'white',
                                '&:hover': {
                                    background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                },
                                transition: 'all 0.3s ease',
                                boxShadow: `0 4px 15px ${currentTheme.primary}50`,
                            }}
                        >
                            <ChevronLeft />
                        </IconButton>
                        <TextField
                            label="Select Date"
                            type="date"
                            value={selectedDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <CalendarToday sx={{ color: currentTheme.primary }} />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{ 
                                minWidth: 200,
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 3,
                                    '&:hover fieldset': {
                                        borderColor: currentTheme.primary,
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: currentTheme.primary,
                                    },
                                }
                            }}
                        />
                        <IconButton 
                            onClick={handleNextDay}
                            disabled={selectedDate >= getTodayLocal()}
                            sx={{
                                background: selectedDate >= getTodayLocal() 
                                    ? 'rgba(0,0,0,0.12)' 
                                    : `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                color: 'white',
                                '&:hover': {
                                    background: selectedDate >= getTodayLocal()
                                        ? 'rgba(0,0,0,0.12)'
                                        : `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                },
                                transition: 'all 0.3s ease',
                                boxShadow: `0 4px 15px ${currentTheme.primary}50`,
                                '&:disabled': {
                                    color: 'rgba(255,255,255,0.5)',
                                }
                            }}
                        >
                            <ChevronRight />
                        </IconButton>
                        
                        <Tooltip title="Go to Today">
                            <Button
                                onClick={handleTodayClick}
                                startIcon={<TodayIcon />}
                                variant="contained"
                                sx={{
                                    background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                    color: 'white',
                                    borderRadius: 3,
                                    px: 3,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    boxShadow: `0 4px 15px ${currentTheme.primary}50`,
                                    '&:hover': {
                                        background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                    }
                                }}
                            >
                                Today
                            </Button>
                        </Tooltip>
                        
                        <Tooltip title="Refresh Data">
                            <IconButton 
                                onClick={handleRefresh} 
                                disabled={isLoading}
                                sx={{
                                    background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                    color: 'white',
                                    '&:hover': {
                                        background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                        transform: 'rotate(180deg)',
                                    },
                                    transition: 'all 0.5s ease',
                                    boxShadow: `0 4px 15px ${currentTheme.primary}50`,
                                }}
                            >
                            <Refresh />
                        </IconButton>
                        </Tooltip>
                        
                        <Tooltip title={isLiveMode ? "Disable Live Mode" : "Enable Live Mode"}>
                            <IconButton 
                                onClick={() => setIsLiveMode(!isLiveMode)}
                                sx={{
                                    background: isLiveMode 
                                        ? `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`
                                        : 'rgba(0,0,0,0.12)',
                                    color: isLiveMode ? 'white' : 'text.secondary',
                                    '&:hover': {
                                        background: isLiveMode 
                                            ? `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`
                                            : 'rgba(0,0,0,0.2)',
                                    },
                                    transition: 'all 0.3s ease',
                                    boxShadow: isLiveMode ? `0 4px 15px ${currentTheme.primary}50` : 'none',
                                }}
                            >
                                {isLiveMode ? <Pause /> : <PlayArrow />}
                            </IconButton>
                        </Tooltip>
                        
                        <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
                            <IconButton 
                                onClick={handleFullscreenToggle}
                                sx={{
                                    background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                    color: 'white',
                                    '&:hover': {
                                        background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100())`,
                                    },
                                    transition: 'all 0.3s ease',
                                    boxShadow: `0 4px 15px ${currentTheme.primary}50`,
                                }}
                            >
                                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                            </IconButton>
                        </Tooltip>
                        
                        <Chip 
                            icon={<CalendarToday />}
                            label={`Last updated: ${lastUpdated.toLocaleTimeString()}`}
                            sx={{ 
                                ml: "auto",
                                background: darkMode ? 'rgba(255,255,255,0.1)' : `linear-gradient(135deg, ${currentTheme.primary}15 0%, ${currentTheme.secondary}15 100%)`,
                                fontWeight: 500,
                                borderRadius: 3,
                                px: 1
                            }}
                        />
                        {!isLoading && data.length > 0 && (
                            <Chip 
                                label={`${data.length}/${expectedDataPoints} data points`}
                                size="small"
                                sx={{ 
                                    background: data.length === expectedDataPoints 
                                        ? 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)' 
                                        : 'linear-gradient(135deg, #ff9800 0%, #ff5722 100%)',
                                    color: 'white',
                                    fontWeight: 600,
                                    borderRadius: 2
                                }}
                            />
                        )}
                    </Box>

                    <Box sx={{ 
                        display: "flex", 
                        flexWrap: "wrap", 
                        gap: 2, 
                        mb: 3,
                        p: 2,
                        background: 'rgba(102, 126, 234, 0.05)',
                        borderRadius: 3,
                        border: '1px solid rgba(102, 126, 234, 0.1)'
                    }}>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                            <Box
                                sx={{
                                    width: 20,
                                    height: 20,
                                    backgroundColor: "rgba(76, 175, 80, 0.3)",
                                    border: "2px solid #4caf50",
                                    borderRadius: 2,
                                    mr: 1.5,
                                }}
                            />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>Electricity Connected</Typography>
                        </Box>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                            <Box
                                sx={{
                                    width: 20,
                                    height: 20,
                                    backgroundColor: "rgba(244, 67, 54, 0.3)",
                                    border: "2px solid #f44336",
                                    borderRadius: 2,
                                    mr: 1.5,
                                }}
                            />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>Electricity Disconnected</Typography>
                        </Box>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                            <Box
                                sx={{
                                    width: 20,
                                    height: 20,
                                    backgroundColor: "rgba(255, 152, 0, 0.3)",
                                    border: "2px solid #ff9800",
                                    borderRadius: 2,
                                    mr: 1.5,
                                }}
                            />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>System Off</Typography>
                        </Box>
                        {missingDataGaps.length > 0 && (
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                                <Box
                                    sx={{
                                        width: 20,
                                        height: 20,
                                        backgroundColor: "rgba(255, 0, 0, 0.15)",
                                        border: "2px dashed #f44336",
                                        borderRadius: 2,
                                        mr: 1.5,
                                    }}
                                />
                                <Typography variant="body2" sx={{ fontWeight: 500, color: '#f44336' }}>
                                    ⚠️ Missing Data ({missingDataGaps.length} gaps)
                                </Typography>
                            </Box>
                        )}
                    </Box>

                    {isLoading ? (
                        <Box sx={{ display: "flex", flexDirection: 'column', justifyContent: "center", alignItems: "center", height: 400 }}>
                            <Refresh sx={{ 
                                animation: "spin 1s linear infinite", 
                                fontSize: 60, 
                                color: "#667eea",
                                mb: 2
                            }} />
                            <Typography variant="h6" sx={{ color: '#667eea', fontWeight: 500 }}>
                                Loading data...
                            </Typography>
                        </Box>
                    ) : (
                        <ResponsiveContainer width="100%" height={450} minHeight={300}>
                            <AreaChart data={data} margin={{ top: 20, right: 10, left: -20, bottom: 20 }}>
                                <defs>
                                    <linearGradient id="pvColor" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.9} />
                                        <stop offset="95%" stopColor="#82ca9d" stopOpacity={0.1} />
                                    </linearGradient>
                                    <linearGradient id="loadColor" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.9} />
                                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>

                                {modeZones.map((zone, index) => (
                                    <ReferenceArea
                                        key={index}
                                        x1={data[zone.start]?.time}
                                        x2={data[zone.end]?.time}
                                        fill={getModeColor(zone.mode)}
                                        strokeOpacity={0.3}
                                    />
                                ))}

                                {/* Missing data gaps visualization */}
                                {missingDataGaps.map((gap, index) => (
                                    <ReferenceArea
                                        key={`gap-${index}`}
                                        x1={gap.start}
                                        x2={gap.end}
                                        fill="rgba(255, 0, 0, 0.15)"
                                        stroke="rgba(255, 0, 0, 0.5)"
                                        strokeWidth={2}
                                        strokeDasharray="5 5"
                                        label={{
                                            value: `⚠️ ${formatMissingDuration(gap.duration)} missing`,
                                            position: 'insideTop',
                                            fill: '#f44336',
                                            fontSize: 11,
                                            fontWeight: 600
                                        }}
                                    />
                                ))}

                                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" opacity={0.5} />
                                <XAxis 
                                    dataKey="time" 
                                    tick={{ fill: '#666', fontSize: 12 }}
                                    stroke="#999"
                                />
                                <YAxis 
                                    tickFormatter={(value) => `${value / 1000}k`}
                                    tick={{ fill: '#666', fontSize: 12 }}
                                    stroke="#999"
                                />
                                <RechartsTooltip content={<CustomTooltip />} />
                                <Legend 
                                    wrapperStyle={{ 
                                        paddingTop: '20px',
                                        fontSize: '14px',
                                        fontWeight: 500
                                    }}
                                />

                                <Area
                                    type="monotone"
                                    dataKey="pv_power"
                                    stroke="#82ca9d"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#pvColor)"
                                    name="PV Power (W)"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="load_power"
                                    stroke="#8884d8"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#loadColor)"
                                    name="Load Power (W)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    )}
                </CardContent>
            </Card>
        </Box>
    );
}