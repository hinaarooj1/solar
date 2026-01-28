import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Card,
    CardContent,
    TextField,
    Button,
    Typography,
    Stack
} from '@mui/material';
import axios from 'axios';
import { toast } from 'react-toastify';
import { API_ENDPOINTS } from '../constants';

const Login = ({ onLogin }) => {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        username: '',
        password: '',
        secret: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (event) => {
        setForm((prev) => ({
            ...prev,
            [event.target.name]: event.target.value
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!form.username || !form.password || !form.secret) {
            toast.error('Please fill in all fields');
            return;
        }
        try {
            setIsSubmitting(true);
            const response = await axios.post(API_ENDPOINTS.login(), form);
            const token = response.data?.access_token;
            if (token) {
                onLogin(token);
                toast.success('Logged in successfully');
                navigate('/', { replace: true });
            } else {
                toast.error('Login failed. Please try again.');
            }
        } catch (error) {
            const message =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                'Unable to login';
            toast.error(message);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                p: 2
            }}
        >
            <Card
                sx={{
                    maxWidth: 420,
                    width: '100%',
                    borderRadius: 4,
                    boxShadow: '0 20px 45px rgba(0,0,0,0.25)'
                }}
            >
                <CardContent sx={{ p: 4 }}>
                    <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, textAlign: 'center' }}>
                        Solar Dashboard Login
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 4, textAlign: 'center', opacity: 0.7 }}>
                        Enter your account credentials and secret key to continue.
                    </Typography>

                    <Stack spacing={3} component="form" onSubmit={handleSubmit}>
                        <TextField
                            label="Username"
                            name="username"
                            value={form.username}
                            onChange={handleChange}
                            fullWidth
                            required
                        />
                        <TextField
                            label="Password"
                            name="password"
                            type="password"
                            value={form.password}
                            onChange={handleChange}
                            fullWidth
                            required
                        />
                        <TextField
                            label="Secret"
                            name="secret"
                            value={form.secret}
                            onChange={handleChange}
                            fullWidth
                            helperText="Provided by the administrator after payment verification"
                            required
                        />
                        <Button
                            type="submit"
                            variant="contained"
                            size="large"
                            disabled={isSubmitting}
                            sx={{
                                textTransform: 'none',
                                fontWeight: 600,
                                py: 1.5,
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                '&:hover': {
                                    background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
                                }
                            }}
                        >
                            {isSubmitting ? 'Signing in...' : 'Sign In'}
                        </Button>
                    </Stack>
                </CardContent>
            </Card>
        </Box>
    );
};

export default Login;

