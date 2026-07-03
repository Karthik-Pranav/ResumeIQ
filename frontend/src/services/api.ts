import axios from "axios";
import { AnalysisResponse } from "@/types/api";

import { AxiosProgressEvent } from "axios";

export async function analyzeResume(
  file: File, 
  jobDescription: string,
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("resume", file);
  formData.append("job_description", jobDescription);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL 
    ? `${process.env.NEXT_PUBLIC_API_URL}/analyze`
    : "http://127.0.0.1:8000/analyze";

  const response = await axios.post<AnalysisResponse>(
    apiUrl,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    }
  );
  return response.data;
}
