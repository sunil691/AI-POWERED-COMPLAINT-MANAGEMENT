import { configureStore } from "@reduxjs/toolkit";
import complaintFormReducer from "./complaintFormSlice";
import chatReducer from "./chatSlice";

export const store = configureStore({
  reducer: {
    complaintForm: complaintFormReducer,
    chat: chatReducer,
  },
});
