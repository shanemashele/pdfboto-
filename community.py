import streamlit as st
import pandas as pd

MESSAGE_FILE = "messages.csv"

# Function to load messages
def load_messages():
    try:
        return pd.read_csv(MESSAGE_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "message"])

# Function to save messages
def save_messages(messages):
    messages.to_csv(MESSAGE_FILE, index=False)

# Function to post a new message
def post_message(username, message):
    messages = load_messages()
    new_message = pd.DataFrame({"username": [username], "message": [message]})
    messages = pd.concat([messages, new_message], ignore_index=True)
    save_messages(messages)
    return messages

# Function to update a message
def update_message(username, index, new_message):
    messages = load_messages()
    if index < len(messages) and messages.at[index, "username"] == username:
        messages.at[index, "message"] = new_message
        save_messages(messages)
        return messages
    else:
        return "You can only update your own messages."

# Function to delete a message
def delete_message(username, index):
    messages = load_messages()
    if index < len(messages) and messages.at[index, "username"] == username:
        messages = messages.drop(index).reset_index(drop=True)
        save_messages(messages)
        return messages
    else:
        return "You can only delete your own messages."

# Function to show community messages with enhanced UI
def show_community():
    st.subheader("Student Community")

    # Message posting section
    message = st.text_area("Share something:", key="community_message")
    if st.button("Post"):
        if message:
            post_message(st.session_state.username, message)
            st.success("Message posted!")
            st.experimental_rerun()  # Refresh to show the new message
        else:
            st.error("Message cannot be empty.")

    # Display community messages
    st.subheader("Community Messages")
    messages = load_messages()
    
    for index, row in messages.iterrows():
        col1, col2, col3 = st.columns([0.1, 1, 0.1])
        
        with col2:
            st.write(f"**{row['username']}:** {row['message']}")

            if st.session_state.username == row['username']:
                if st.button("Update", key=f"update-{index}"):
                    st.session_state.editing_message = {"index": index, "message": row['message']}
                    st.experimental_rerun()

                if st.button("Delete", key=f"delete-{index}"):
                    delete_message(row['username'], index)
                    st.success("Message deleted!")
                    st.experimental_rerun()

    # Message updating section
    if "editing_message" in st.session_state:
        index = st.session_state.editing_message["index"]
        old_message = st.session_state.editing_message["message"]

        st.subheader("Update Your Message")
        updated_message = st.text_area("Update your message:", value=old_message, key="update_message")
        
        if st.button("Confirm Update"):
            update_message(st.session_state.username, index, updated_message)
            st.success("Message updated!")
            del st.session_state.editing_message  # Clear the editing state
            st.experimental_rerun()

        if st.button("Cancel Update"):
            del st.session_state.editing_message  # Clear the editing state
            st.experimental_rerun()

# Sample usage
if __name__ == "__main__":
    st.title("Student Community")
    
    # Mock user authentication
    st.session_state.username = "student1"  # This should come from the authentication system
    
    show_community()
