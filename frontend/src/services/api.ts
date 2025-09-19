import axios from 'axios';
import { DashboardData, ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for file processing (AI analysis takes time)
});

export const uploadFile = async (file: File): Promise<DashboardData> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timed out. The AI analysis is taking longer than expected. Please try again with a smaller file or check your internet connection.');
      }
      if (error.response?.status === 500) {
        throw new Error('Server error during processing. Please check the backend logs for more details.');
      }
      throw new Error(error.response?.data?.detail || 'Failed to upload file');
    }
    throw new Error('An unexpected error occurred');
  }
};

export const getHealth = async (): Promise<{ status: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('API is not available');
  }
};

export const getMetrics = async (): Promise<{ available_metrics: string[] }> => {
  try {
    const response = await api.get('/metrics');
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch metrics');
  }
};
