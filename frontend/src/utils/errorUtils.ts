/**
 * Utility to extract human-readable error messages from API responses
 * Handles FastAPI validation errors (422) which return a list of error objects
 */
export const getErrorMessage = (error: any): string => {
    if (!error.response) {
        return error.message || 'Network error. Please check your connection.';
    }

    const detail = error.response.data?.detail;

    // Cases where detail is a simple string (standard HTTPException)
    if (typeof detail === 'string') {
        return detail;
    }

    // Cases where detail is an array (FastAPI/Pydantic validation errors)
    if (Array.isArray(detail)) {
        return detail
            .map((err: any) => {
                // loc is usually something like ['body', 'field_name'] or ['query', 'param']
                const field = err.loc && err.loc.length > 1 ? err.loc.slice(1).join('.') : err.loc?.[0];
                return field ? `${field}: ${err.msg}` : err.msg;
            })
            .join('; ');
    }

    // Handle other object formats if any
    if (detail && typeof detail === 'object') {
        return detail.msg || detail.message || JSON.stringify(detail);
    }

    // Fallback to general response data or status text
    return error.response.data?.message || error.response.statusText || 'An unexpected error occurred';
};
