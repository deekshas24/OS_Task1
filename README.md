# OS Task 1 — Multithreading

This repository contains the programs developed for the Operating Systems
multithreading assignment.
The assignment covers two different situations where threads are useful. The
first program deals with two threads sharing a common buffer. The second
program breaks a matrix multiplication into smaller cell-level calculations
and handles them using a thread pool.

---

## Contents

* [Producer-Consumer](#1-producer-consumer)
* [Matrix Multiplication](#2-matrix-multiplication)
* [Animation](#3-matrix-multiplication-animation)
* [Requirements](#4-requirements)
* [How to Run](#5-how-to-run)
* [What This Assignment Demonstrates](#6-what-this-assignment-demonstrates)

---

## Project Layout

```text
OS_Task1/
│
├── producerconsumer/
│   ├── Buffer.java
│   ├── Producer.java
│   ├── Consumer.java
│   └── ProducerConsumer.java
│
├── matrix_multiplication_animation.py
├── matrix_multiplication.gif
└── README.md
```

---

# 1. Producer-Consumer

The first program is a simple implementation of the Producer-Consumer
problem using Java threads.

There are two threads:

* **Producer** — creates values from 1 to 10.
* **Consumer** — removes those values from the shared buffer.

The two threads use the same `Buffer` object. The buffer has a maximum
capacity of **5 values**.

Because both threads access the same data, the buffer needs to be protected
from simultaneous access.

### The shared buffer

`Buffer.java` uses a `Queue<Integer>` implemented with `LinkedList`.

```java
private final Queue<Integer> buffer = new LinkedList<>();
```

The `produce()` and `consume()` methods are declared as `synchronized`.
This means that a thread must have access to the buffer's monitor before it
can execute either operation.

When there is no space left in the buffer, the Producer waits:

```java
while (buffer.size() == capacity) {
    wait();
}
```

Likewise, the Consumer waits when there is nothing available:

```java
while (buffer.isEmpty()) {
    wait();
}
```

After adding or removing an item, the thread calls:

```java
notifyAll();
```

This allows any thread waiting on the same buffer to check the condition
again.

### Producer

`Producer.java` extends `Thread` and produces ten values:

```text
1, 2, 3, ... 10
```

A small delay is added between productions using:

```java
Thread.sleep(200);
```

If the thread is interrupted, the interruption is restored using
`Thread.currentThread().interrupt()`.

### Consumer

`Consumer.java` also extends `Thread` and consumes ten values from the
buffer.

It waits for a short period after consuming each value:

```java
Thread.sleep(350);
```

Since the Producer and Consumer have different delays, the output order can
vary from one execution to another.

### Starting the threads

`ProducerConsumer.java` creates the shared buffer and starts both threads:

```java
Buffer buffer = new Buffer(5);

Producer producer = new Producer(buffer);
Consumer consumer = new Consumer(buffer);

producer.start();
consumer.start();
```

The `main()` method then uses `join()` so that it waits for both threads to
finish before printing:

```text
Execution completed.
```

---

## Running the Java Program

From the project directory:

### Compile

```bash
javac producerconsumer/*.java
```

### Run

```bash
java producerconsumer.ProducerConsumer
```

### Example output

```text
Produced: 1
Consumed: 1
Produced: 2
Produced: 3
Consumed: 2
Produced: 4
Consumed: 3
...
Execution completed.
```

The exact sequence is not fixed because both threads are executing
concurrently.

---

# 2. Matrix Multiplication

The second program performs multiplication of two **100 × 100 matrices**.

Both input matrices are generated using TensorFlow. Since the resulting
matrix also has 100 × 100 positions, there are:

```text
100 × 100 = 10,000 cells
```

The program treats every result cell as a separate task.

The basic calculation is:

```text
Matrix A × Matrix B
        ↓
    Matrix C
```

To calculate one position in Matrix C, the program takes one complete row
from Matrix A and one complete column from Matrix B.

For example:

```python
row_data = matrix_a[row, :]
column_data = matrix_b[:, column]
```

The two vectors are multiplied element by element and then summed using
TensorFlow:

```python
value = tf.reduce_sum(row_data * column_data)
```

The calculated value is then placed into the corresponding position of the
result matrix.

---

## Creating the Input Matrices

The `create_matrix()` function generates a 100 × 100 TensorFlow matrix.

The values are random integers from **1 to 19**:

```python
tf.random.uniform(
    shape=(SIZE, SIZE),
    minval=1,
    maxval=20,
    dtype=tf.int32
)
```

Since the matrices are generated randomly, the result will be different
each time the program is executed.

---

## Breaking the Work into Tasks

The program uses `ThreadPoolExecutor` instead of creating a new thread for
every matrix cell.

The number of workers is obtained from the available CPU cores:

```python
workers = os.cpu_count() or 4
```

Every `(row, column)` combination is submitted to the executor:

```text
(0, 0)
(0, 1)
(0, 2)
...
(99, 99)
```

This results in **10,000 submitted tasks**.

The executor manages the available worker threads and assigns the pending
tasks to them.

Once all tasks have completed, the program calculates and prints the total
execution time.

---

## Checking the Result

After the multiplication finishes, the program prints the first 3 × 3
portion of Matrix C.

For example:

```text
First 3 x 3 part of the result:
[9977, 9301, 10034]
[9267, 9709, 10129]
[10500, 10056, 10206]
```

These numbers are only examples. They change when the randomly generated
input matrices change.

---

# 3. Matrix Multiplication Animation

Along with calculating the result, the program records the order in which
the matrix cells finish.

The `ProgressLog` class is responsible for maintaining this information.

```python
class ProgressLog:

    def __init__(self):
        self.cells = []
        self.lock = threading.Lock()
```

Whenever a cell is completed, its row and column are added to the list.

Because several worker threads can finish at the same time, a
`threading.Lock()` is used while updating the list:

```python
with self.lock:
    self.cells.append((row, column))
```

This keeps the execution record safe when it is accessed by multiple
threads.

### Why record the completion order?

The animation does not simply fill Matrix C from left to right or from top
to bottom.

Instead, it uses the **actual order in which the worker tasks completed**.

This makes the animation connected to the threaded execution of the
program.

---

## What the GIF Shows

The animation contains three panels.

### Matrix A

A horizontal red marker indicates the row being used.

### Matrix B

A vertical red marker indicates the column being used.

### Matrix C

The result cells become visible as their corresponding calculations are
completed.

The idea being shown is:

```text
        Row from A
             │
             │
             ▼
       Dot Product
             │
             ▲
             │
        Column from B
             │
             ▼
        Cell in C
```

The animation processes **25 completed cells per frame**, so all 10,000
cells do not appear one at a time.

A progress message at the bottom also shows information such as:

```text
Cells completed: 250/10000    C[42][17]
```

The highlighted row and column correspond to the most recently processed
cell in that animation frame.

---

## GIF File

The generated animation is saved as:

```text
matrix_multiplication.gif
```

It is included in this repository so the visualization can be viewed
directly without running the Python program again.

---

# 4. Requirements

## Java

* JDK 8 or later

The Producer-Consumer program only uses standard Java classes, so no
additional Java libraries are required.

## Python

The matrix program requires:

* Python 3.x
* TensorFlow
* NumPy
* Matplotlib
* Pillow

Install the required packages with:

```bash
pip install tensorflow numpy matplotlib pillow
```

---

# 5. How to Run

## Producer-Consumer

Compile the Java files:

```bash
javac producerconsumer/*.java
```

Then run:

```bash
java producerconsumer.ProducerConsumer
```

---

## Matrix Multiplication

Run:

```bash
python matrix_multiplication_animation.py
```

The program will:

1. Generate two random 100 × 100 matrices.
2. Create a task for every result cell.
3. Process the tasks using `ThreadPoolExecutor`.
4. Calculate each cell using TensorFlow.
5. Record the order in which cells finish.
6. Print the execution time and part of the result.
7. Display the matrix animation.
8. Save the animation as `matrix_multiplication.gif`.

---

# 6. What This Assignment Demonstrates

The two programs approach multithreading from different directions.

### Producer-Consumer

The Java program demonstrates:

* Creating threads
* Sharing data between threads
* Synchronization
* Waiting for a resource
* Notifying waiting threads
* Managing a bounded queue
* Using `join()` to wait for thread completion

### Matrix Multiplication

The Python program demonstrates:

* Thread pools
* Breaking a larger computation into smaller tasks
* Concurrent task execution
* TensorFlow operations
* Thread-safe access to shared execution information
* Measuring execution time
* Visualizing task completion

---

# Conclusion

This assignment demonstrates how multithreading can be used for both synchronized data sharing and parallel computation. The Producer-Consumer problem focuses on thread coordination and synchronization, while matrix multiplication demonstrates task parallelism using a thread pool. The animation further helps visualize how the result is built as the parallel tasks complete.
