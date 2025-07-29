export default class Chat {
    constructor() {
        this.chat = document.querySelector(".great-ds-chat");

        this.apiEndpoints = JSON.parse(this.chat.getAttribute('data-api'));

        this.submitButton = document.querySelector(".great-ds-chat__input-button");

        this.emptyAgentMessageContainer = document.querySelector("#empty-agent-message");
        this.emptyUserMessageContainer = document.querySelector("#empty-user-message");

        this.messagesContainer = document.querySelector(".great-ds-chat__messages-container");

        this.messageInput = document.querySelector(".great-ds-chat__input");
        this.apiToken='';

        this.init();
    };
    init() {
        this.handleStartChat();

        this.submitButton.addEventListener("click", (e) => {
            e.stopPropagation();
            this.handleSubmitChat();
        });
    }

    async handleStartChat() {

      // Try to find pre-existing chat, if not begin a new chat and return the starting info
      try {
          const response = await fetch(this.apiEndpoints['start'], {
              method: 'POST',
              headers: {
                  'Accept': 'application/json',
                  'X-Requested-With': 'XMLHttpRequest',
                  'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
              }
          });
          let data = await response.json()

          return data;
      } catch (error) {
          console.error('There was a problem with the start operation:', error);
      }
    }
    async handleSubmitChat() {
      let currentMessage = this.messageInput.value;
      this.addChatToHistory('user', currentMessage);
      try {
          const response = await fetch(this.apiEndpoints['send'], {
              method: 'POST',
              headers: {
                  'Accept': 'application/json',
                  'X-Requested-With': 'XMLHttpRequest',
              },
              body: JSON.stringify({"message": currentMessage}),
          });
          this.handleReceiveChat()
      } catch (error) {
          console.error('There was a problem with the send operation:', error);
      }
    }

    async handleReceiveChat() {
        try {
            const response = await fetch(this.apiEndpoints['receive'], {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
             })
            .then(response => {return response.json()})
            .then(data => {console.log(data)
                this.addChatToHistory('agent', data.text)
            })
            ;
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
      }


    async handleEndChat() {

        // Try to find pre-existing chat, if not begin a new chat and return the starting info
        try {
            /**
            const response = await fetch(apiEndpoints['end'], {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            */
            console.log('chat over')
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
      }

    addChatToHistory(sender, text) {
      let newMessageContainer = this.emptyUserMessageContainer.cloneNode(true);
      console.log('new')
      newMessageContainer.classList.remove('great-ds-hidden')
      let newMessage = newMessageContainer.querySelector(".great-ds-chat__message")

      newMessageContainer.classList.add('great-ds-chat__message-container--'.concat(sender))
      newMessage.innerHTML = text;

      this.messagesContainer.appendChild(newMessageContainer)
    }
  }
  document.addEventListener("DOMContentLoaded", () => {
    new Chat();
  });