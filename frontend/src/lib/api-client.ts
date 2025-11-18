/**
 * API client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Add /api/v1 prefix if not already present
    const normalizedEndpoint = endpoint.startsWith("/api/v1") 
      ? endpoint 
      : `${API_V1_PREFIX}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
    const url = `${this.baseUrl}${normalizedEndpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        // Don't set Content-Type for FormData (browser will set it with boundary)
        ...(options.body instanceof FormData
          ? {}
          : { "Content-Type": "application/json" }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = response.statusText || "Request failed";
      try {
        const errorData = await response.json();
        // Try multiple possible error message fields
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData?.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        } else if (errorData?.message) {
          errorMessage = typeof errorData.message === 'string' ? errorData.message : JSON.stringify(errorData.message);
        } else if (errorData?.error) {
          errorMessage = typeof errorData.error === 'string' ? errorData.error : JSON.stringify(errorData.error);
        } else {
          errorMessage = JSON.stringify(errorData);
        }
      } catch (parseError) {
        // If JSON parsing fails, try to get text
        try {
          const text = await response.text();
          errorMessage = text || response.statusText || "Request failed";
        } catch {
          errorMessage = response.statusText || "Request failed";
        }
      }
      const error = new Error(errorMessage);
      (error as any).response = response;
      throw error;
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data instanceof FormData ? data : data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

export const apiClient = new ApiClient();
