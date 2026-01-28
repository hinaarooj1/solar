import React, { useState } from "react";
import axios from "axios";
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    Legend
} from "recharts";
import {
    Box,
    Card,
    CardContent,
    Grid,
    InputAdornment,
    TextField,
    LinearProgress,
    Fade,
    IconButton,
    Button,
    Typography
} from "@mui/material";
import {
    SolarPower as SolarIcon,
    CalendarToday,
    Refresh,
    TrendingUp,
    BatteryChargingFull
} from "@mui/icons-material";
import { toast } from "react-toastify";
import { API_ENDPOINTS } from "../constants";

const MonthlyStats = ({ darkMode, themeColor, themeColors }) => {
    const today = new Date().toISOString().split("T")[0];
    const firstDay = new Date();
    firstDay.setDate(1);
    const defaultFrom = firstDay.toISOString().split("T")[0];

    const [fromDate, setFromDate] = useState(defaultFrom);
    const [toDate, setToDate] = useState(today);

    const [data, setData] = useState([]);
    const [totals, setTotals] = useState({
        production: '...',
        load: '...',
        saved: '...',
        feeded: '...',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [missingDates, setMissingDates] = useState([]);
    const [isError, setisError] = useState("");
    const [progress, setProgress] = useState(0);
    
    const currentTheme = themeColors[themeColor];
    
    const fetchData = async () => {
        try {
            setTotals({
                production: '...',
                load: '...',
                saved: '...',
                feeded: '...',
            });
            setIsLoading(true);
            setProgress(0);

            const res = await axios.get(
                API_ENDPOINTS.getStatsRange(fromDate, toDate),
                {
                    onDownloadProgress: (progressEvent) => {
                        if (progressEvent.event.target.responseText) {
                            const chunks = progressEvent.event.target.responseText.trim().split('\n');
                            const lastChunk = chunks[chunks.length - 1];

                            try {
                                const data = JSON.parse(lastChunk);
                                if (data.success && data.progress !== undefined) {
                                    setProgress(data.progress);
                                }
                            } catch (e) {
                                // Ignore parsing errors for incomplete chunks
                            }
                        }
                    }
                }
            );
            console.log('res: ', res);
            
            const lines = res.data.trim().split('\n');
            const dailyStats = [];
            let finalTotals = { total_production_kwh: 0, total_load_kwh: 0 };

            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const data = JSON.parse(line);
                        if (data.success) {
                            if (data.daily) {
                                dailyStats.push(data.daily);
                            }
                            if (data.total_production_kwh !== undefined) {
                                finalTotals.total_production_kwh = data.total_production_kwh;
                            }
                            if (data.total_load_kwh !== undefined) {
                                finalTotals.total_load_kwh = data.total_load_kwh;
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing JSON chunk:', e);
                    }
                }
            }

            const dailyData = dailyStats.map((d) => {
                const isNull = (d.production_kwh === null || d.load_kwh === null);

                if (isNull) {
                    console.warn(`⚠️ No data for ${d.date}`);
                }

                return {
                    date: d.date,
                    production: isNull ? 0 : d.production_kwh,
                    load: isNull ? 0 : d.load_kwh,
                    saved: isNull ? 0 : Math.min(d.production_kwh, d.load_kwh),
                    feeded: isNull ? 0 : Math.max(0, d.production_kwh - d.load_kwh),
                    isNull
                };
            });

            setData(dailyData);

            const totalProd = finalTotals.total_production_kwh;
            const totalLoad = finalTotals.total_load_kwh;
            const saved = Math.min(totalProd, totalLoad);
            const feeded = Math.max(0, totalProd - totalLoad);

            setTotals({
                production: totalProd.toFixed(2),
                load: totalLoad.toFixed(2),
                saved: saved.toFixed(2),
                feeded: feeded.toFixed(2),
            });

            const nullDays = dailyData.filter(d => d.isNull).map(d => d.date);
            setMissingDates(nullDays);

        } catch (err) {
            setisError(err)
            toast.error("Error fetching API")
            console.error("Error fetching API:", err);
            setTotals({
                production: 0,
                load: 0,
                saved: 0,
                feeded: 0,
            });
        } finally {
            setIsLoading(false);
            setProgress(0);
        }
    };

    return (
        <Box>
            <Grid container spacing={{ xs: 2, sm: 2, md: 3 }} sx={{ mb: { xs: 2, sm: 3 } }}>
                <Grid item xs={12} sm={6} md={4}>
                    <Fade in timeout={500}>
                        <Card sx={{
                            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            color: "white",
                            borderRadius: 4,
                            boxShadow: "0 10px 40px rgba(102, 126, 234, 0.3)",
                            transition: "all 0.3s ease",
                            "&:hover": {
                                transform: "translateY(-8px)",
                                boxShadow: "0 15px 50px rgba(102, 126, 234, 0.4)",
                            }
                        }}>
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ 
                                        opacity: 0.9, 
                                        textTransform: 'uppercase', 
                                        letterSpacing: 1,
                                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                                    }}>
                                        Total Production
                                    </Typography>
                                    <SolarIcon sx={{ fontSize: { xs: 28, sm: 32 }, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ 
                                    fontWeight: 700, 
                                    mb: 1,
                                    fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
                                }}>
                                    {totals.production}
                                </Typography>
                                <Typography variant="h6" sx={{ 
                                    opacity: 0.9,
                                    fontSize: { xs: '1rem', sm: '1.25rem' }
                                }}>
                                    kWh
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <Fade in timeout={700}>
                        <Card sx={{
                            background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                            color: "white",
                            borderRadius: 4,
                            boxShadow: "0 10px 40px rgba(240, 147, 251, 0.3)",
                            transition: "all 0.3s ease",
                            "&:hover": {
                                transform: "translateY(-8px)",
                                boxShadow: "0 15px 50px rgba(240, 147, 251, 0.4)",
                            }
                        }}>
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ 
                                        opacity: 0.9, 
                                        textTransform: 'uppercase', 
                                        letterSpacing: 1,
                                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                                    }}>
                                        Total Load
                                    </Typography>
                                    <TrendingUp sx={{ fontSize: { xs: 28, sm: 32 }, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ 
                                    fontWeight: 700, 
                                    mb: 1,
                                    fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
                                }}>
                                    {totals.load}
                                </Typography>
                                <Typography variant="h6" sx={{ 
                                    opacity: 0.9,
                                    fontSize: { xs: '1rem', sm: '1.25rem' }
                                }}>
                                    kWh
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
                <Grid item xs={12} sm={12} md={4}>
                    <Fade in timeout={900}>
                        <Card sx={{
                            background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                            color: "white",
                            borderRadius: 4,
                            boxShadow: "0 10px 40px rgba(79, 172, 254, 0.3)",
                            transition: "all 0.3s ease",
                            "&:hover": {
                                transform: "translateY(-8px)",
                                boxShadow: "0 15px 50px rgba(79, 172, 254, 0.4)",
                            }
                        }}>
                            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                    <Typography variant="body2" sx={{ 
                                        opacity: 0.9, 
                                        textTransform: 'uppercase', 
                                        letterSpacing: 1,
                                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                                    }}>
                                        Fed to Grid
                            </Typography>
                                    <BatteryChargingFull sx={{ fontSize: { xs: 28, sm: 32 }, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" sx={{ 
                                    fontWeight: 700, 
                                    mb: 1,
                                    fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
                                }}>
                                    {totals.feeded}
                                </Typography>
                                <Typography variant="h6" sx={{ 
                                    opacity: 0.9,
                                    fontSize: { xs: '1rem', sm: '1.25rem' }
                                }}>
                                    kWh
                            </Typography>
                        </CardContent>
                    </Card>
                    </Fade>
                </Grid>
            </Grid>

            <Card sx={{
                borderRadius: 4,
                background: darkMode ? 'linear-gradient(145deg, #1e1e1e 0%, #2d2d2d 100%)' : 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                border: `1px solid ${darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'}`
            }}>
                <CardContent sx={{ p: { xs: 2, md: 4 } }}>
                    <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
                        <TextField
                            label="From"
                            type="date"
                            value={fromDate}
                            onChange={(e) => setFromDate(e.target.value)}
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
                        <TextField
                            label="To"
                            type="date"
                            value={toDate}
                            onChange={(e) => setToDate(e.target.value)}
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
                            onClick={fetchData} 
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
                        <Button 
                            variant="contained" 
                            onClick={fetchData} 
                            disabled={isLoading}
                            sx={{
                                background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                borderRadius: 3,
                                px: 4,
                                py: 1.5,
                                textTransform: 'none',
                                fontSize: '1rem',
                                fontWeight: 600,
                                boxShadow: `0 4px 15px ${currentTheme.primary}50`,
                                '&:hover': {
                                    background: `linear-gradient(135deg, ${currentTheme.secondary} 0%, ${currentTheme.primary} 100%)`,
                                    boxShadow: `0 6px 20px ${currentTheme.primary}40`,
                                }
                            }}
                        >
                            Confirm
                        </Button>
                    </Box>
                    {missingDates.length > 0 && (
                        <Typography variant="body2" color="error" sx={{ mb: 2, p: 2, background: 'rgba(244, 67, 54, 0.1)', borderRadius: 2 }}>
                            ⚠️ Missing data for: {missingDates.join(", ")}
                        </Typography>
                    )}
                    {isError && (
                        <Typography variant="body2" color="error" sx={{ mb: 2, p: 2, background: 'rgba(244, 67, 54, 0.1)', borderRadius: 2 }}>
                            ⚠️ Error: {isError}
                        </Typography>
                    )}
                    {isLoading ? (
                        <Box sx={{ width: '100%', mb: 2 }}>
                            <LinearProgress
                                variant="determinate"
                                value={progress}
                                sx={{ 
                                    height: 12, 
                                    borderRadius: 6,
                                    background: `rgba(${currentTheme.primary}, 0.1)`,
                                    '& .MuiLinearProgress-bar': {
                                        background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.secondary} 100%)`,
                                        borderRadius: 6,
                                    }
                                }}
                            />
                            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2, fontWeight: 500, fontSize: '1rem' }}>
                                Loading... {progress.toFixed(0)}%
                            </Typography>
                        </Box>
                    ) : (
                        <ResponsiveContainer width="100%" height={450}>
                            <AreaChart data={data}
                                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="prodColor" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.9} />
                                        <stop offset="95%" stopColor="#82ca9d" stopOpacity={0.1} />
                                    </linearGradient>
                                    <linearGradient id="loadColor" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.9} />
                                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" opacity={0.5} />
                                <XAxis 
                                    dataKey="date" 
                                    tick={{ fill: '#666', fontSize: 12 }}
                                    stroke="#999"
                                />
                                <YAxis 
                                    width={40} 
                                    tickFormatter={(value) => `${value}k`}
                                    tick={{ fill: '#666', fontSize: 12 }}
                                    stroke="#999"
                                />
                                <RechartsTooltip />
                                <Legend 
                                    wrapperStyle={{ 
                                        paddingTop: '20px',
                                        fontSize: '14px',
                                        fontWeight: 500
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="production"
                                    stroke="#82ca9d"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#prodColor)"
                                    name="Production (kWh)"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="load"
                                    stroke="#8884d8"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#loadColor)"
                                    name="Load (kWh)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    )}
                </CardContent>
            </Card>
        </Box>
    );
};

export default MonthlyStats;

