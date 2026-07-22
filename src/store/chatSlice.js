import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { createComplaint, sendComplaintMessage, uploadComplaintPdf } from "../api/complaintsApi";
import { applyAiPatch, setComplaintId } from "./complaintFormSlice";

export const sendMessage = createAsyncThunk("chat/sendMessage", async (message, { dispatch, getState, rejectWithValue }) => {
  try {
    let complaintId = getState().complaintForm.complaintId;
    if (!complaintId) {
      const complaint = await createComplaint();
      complaintId = complaint.id;
      dispatch(setComplaintId(complaintId));
    }
    const result = await sendComplaintMessage({ complaint_id: complaintId, message });
    dispatch(applyAiPatch(result));
    return result;
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const uploadPdf = createAsyncThunk("chat/uploadPdf", async (file, { dispatch, getState, rejectWithValue }) => {
  try {
    let complaintId = getState().complaintForm.complaintId;
    if (!complaintId) {
      const complaint = await createComplaint();
      complaintId = complaint.id;
      dispatch(setComplaintId(complaintId));
    }
    const result = await uploadComplaintPdf(file, complaintId);
    if (result.complaint_id && typeof result.complaint_id === "number") dispatch(setComplaintId(result.complaint_id));
    dispatch(applyAiPatch(result));
    return result;
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

const initialState = { messages: [], isLoading: false, error: null };

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ id: crypto.randomUUID(), role: "user", content: action.payload, timestamp: new Date().toISOString() });
    },
    clearChat(state) {
      state.messages = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => { state.isLoading = true; state.error = null; })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages.push({ id: crypto.randomUUID(), role: "assistant", content: action.payload.reply_message, timestamp: new Date().toISOString() });
      })
      .addCase(sendMessage.rejected, (state, action) => { state.isLoading = false; state.error = action.payload || "The copilot could not respond."; })
      .addCase(uploadPdf.pending, (state) => { state.isLoading = true; state.error = null; })
      .addCase(uploadPdf.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages.push({ id: crypto.randomUUID(), role: "assistant", content: action.payload.reply_message, timestamp: new Date().toISOString() });
      })
      .addCase(uploadPdf.rejected, (state, action) => { state.isLoading = false; state.error = action.payload || "The PDF could not be processed."; });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
