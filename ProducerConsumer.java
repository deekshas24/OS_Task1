package producerconsumer;

import java.util.LinkedList;
import java.util.Queue;

public class Buffer {

    private final Queue<Integer> buffer = new LinkedList<>();
    private final int capacity;

    public Buffer(int capacity) {
        this.capacity = capacity;
    }

    // Adds a value when space is available
    public synchronized void produce(int value) throws InterruptedException {

        while (buffer.size() == capacity) {
            wait();
        }

        buffer.add(value);
        System.out.println("Produced: " + value);

        notifyAll();
    }

    // Removes a value when the buffer is not empty
    public synchronized void consume() throws InterruptedException {

        while (buffer.isEmpty()) {
            wait();
        }

        int value = buffer.remove();
        System.out.println("Consumed: " + value);

        notifyAll();
    }
}
package producerconsumer;

public class Producer extends Thread {

    private final Buffer buffer;

    public Producer(Buffer buffer) {
        this.buffer = buffer;
    }

    @Override
    public void run() {

        // Produce ten values
        for (int i = 1; i <= 10; i++) {

            try {
                buffer.produce(i);
                Thread.sleep(200);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
package producerconsumer;

public class Consumer extends Thread {

    private final Buffer buffer;

    public Consumer(Buffer buffer) {
        this.buffer = buffer;
    }

    @Override
    public void run() {

        // Consume ten values
        for (int i = 1; i <= 10; i++) {

            try {
                buffer.consume();
                Thread.sleep(350);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
package producerconsumer;

public class ProducerConsumer {

    public static void main(String[] args) {

        // Shared buffer with a capacity of five
        Buffer buffer = new Buffer(5);

        Producer producer = new Producer(buffer);
        Consumer consumer = new Consumer(buffer);

        // Start both threads
        producer.start();
        consumer.start();

        try {
            // Wait until both threads complete
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("Execution completed.");
    }
}
