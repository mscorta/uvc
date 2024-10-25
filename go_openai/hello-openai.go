///usr/bin/true; exec /usr/bin/env go run "$0" "$@"

package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/joho/godotenv"
	"github.com/sashabaranov/go-openai" // or your preferred OpenAI client
)

type Chatter struct {
	client *openai.Client
}

func NewChatter() Chatter {
	var err error = godotenv.Load(os.Getenv("HOME") + "/.env")
	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	// Get the OpenAI API key from environment variables
	apiKey := os.Getenv("OPENAI_API_KEYS")
	if apiKey == "" {
		log.Fatal("OPENAI_API_KEYS is not set")
	}

	// Initialize the OpenAI client
	var client *openai.Client = openai.NewClient(apiKey)
	return Chatter{client: client}

}

func (chatter *Chatter) getResponse( //
	message string, //
) string {
	client := chatter.client
	messages := []openai.ChatCompletionMessage{
		{
			Role:    openai.ChatMessageRoleUser,
			Content: message,
		},
	}

	response, err := client.CreateChatCompletion( //
		context.Background(), openai.ChatCompletionRequest{
			Model:     openai.GPT3Dot5Turbo, // or openai.GPT4
			Messages:  messages,
			MaxTokens: 10,
		})

	if err != nil {
		log.Fatalf("failed to create chat completion: %v", err)
	}

	// Print the assistant's response
	return response.Choices[0].Message.Content

}

func run(wg *sync.WaitGroup, iterations int) {
	defer wg.Done() // Notify the WaitGroup that this goroutine is done
	var chatter Chatter = NewChatter()

	for i := 0; i < iterations; i++ {
		response := chatter.getResponse("What is the capital of France?")
		fmt.Println(response)
	}
}

func main() {

	var n int = 100 // Number of goroutines
	var iterations int = 1
	var wg sync.WaitGroup

	startTime := time.Now()

	for i := 0; i < n; i++ {
		wg.Add(1)
		go run(&wg, iterations)
	}

	wg.Wait() // Wait for all goroutines to finish

	var duration time.Duration = time.Since(startTime)
	var took float64 = duration.Seconds()
	var calls int = n * iterations
	var reqs float64 = float64(calls) / took

	fmt.Printf("Took %.2f s for %d calls and %.2f requests/s\n", took, calls, reqs)
}
