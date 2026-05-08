import axios from 'axios';
import type { BinNode, Route, HazMatBrief } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
});

export const fetchBins = (): Promise<BinNode[]> =>
  api.get('/bins').then(r => r.data);

export const fetchRoute = (): Promise<Route> =>
  api.get('/route').then(r => r.data);

export const fetchHazmat = (nodeId: string): Promise<HazMatBrief> =>
  api.get(`/hazmat/${nodeId}`).then(r => r.data);
