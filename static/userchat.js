document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".userchat-page");
  if (!page || typeof io === "undefined") {
    return;
  }

  const userEmail = page.dataset.userEmail || "";
  const activeChatId = page.dataset.activeChatId ? Number(page.dataset.activeChatId) : null;
  const chatList = document.querySelector(".userchat-chat-list");
  const messagesContainer = document.querySelector(".userchat-messages");
  const form = document.querySelector(".userchat-input-bar");
  const input = form ? form.querySelector(".userchat-input") : null;

  const socket = io({ transports: ["websocket", "polling"] });

  const chatItems = () =>
    Array.from(document.querySelectorAll(".userchat-chat-item[data-chat-id]"));

  const removePlaceholders = () => {
    if (!messagesContainer) {
      return;
    }
    messagesContainer
      .querySelectorAll("[data-placeholder]")
      .forEach((node) => node.remove());
  };

  const scrollMessagesToBottom = () => {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  };

  const buildMessageNode = (message) => {
    const node = document.createElement("div");
    if (message.message_type === "system") {
      node.className = "userchat-message userchat-message-system";
      node.textContent = message.message_text;
      return node;
    }

    const directionClass =
      message.sender_email === userEmail
        ? "userchat-message-outgoing"
        : "userchat-message-incoming";
    node.className = `userchat-message ${directionClass}`;
    node.textContent = message.message_text;
    return node;
  };

  const updateChatPreview = (message) => {
    const items = chatItems();
    const match = items.find(
      (item) => Number(item.dataset.chatId) === Number(message.chat_id)
    );
    if (!match) {
      return;
    }

    const preview = match.querySelector(".userchat-chat-preview");
    if (preview) {
      preview.textContent = message.message_text;
    }

    if (chatList && match.parentElement === chatList) {
      chatList.prepend(match);
    }
  };

  const appendMessage = (message) => {
    if (!messagesContainer) {
      return;
    }
    removePlaceholders();
    const node = buildMessageNode(message);
    messagesContainer.appendChild(node);
    scrollMessagesToBottom();
  };

  socket.on("connect", () => {
    chatItems().forEach((item) => {
      socket.emit("join_thread", { chat_id: item.dataset.chatId });
    });
  });

  socket.on("chat_message", (message) => {
    updateChatPreview(message);
    if (activeChatId && Number(message.chat_id) === Number(activeChatId)) {
      appendMessage(message);
    }
  });

  if (form && input) {
    form.addEventListener("submit", (event) => {
      if (!socket.connected) {
        return;
      }
      event.preventDefault();
      const text = input.value.trim();
      if (!text) {
        return;
      }

      socket.emit(
        "send_message",
        { chat_id: activeChatId, message: text },
        (response) => {
          if (!response || response.ok === false) {
            form.submit();
            return;
          }
        }
      );

      input.value = "";
    });
  }

  scrollMessagesToBottom();
});
