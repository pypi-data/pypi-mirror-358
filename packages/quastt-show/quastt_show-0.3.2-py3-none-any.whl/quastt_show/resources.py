import time
import traceback
import numpy as np

class SimpleNeuralNet:
    """
    A very simple feed-forward neural network for demonstration.
    Input: vectorized error features
    Output: vector representing categories/suggestions
    """
    def __init__(self, input_size, hidden_sizes, output_size, lr=0.01):
        self.lr = lr
        self.weights = []
        self.biases = []
        layer_sizes = [input_size] + hidden_sizes + [output_size]
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.1
            b = np.zeros(layer_sizes[i+1])
            self.weights.append(w)
            self.biases.append(b)

    def relu(self, x):
        return np.maximum(0, x)

    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=-1, keepdims=True)

    def forward(self, x):
        self.zs = []
        self.activations = [x]
        a = x
        for i in range(len(self.weights) - 1):
            z = a @ self.weights[i] + self.biases[i]
            a = self.relu(z)
            self.zs.append(z)
            self.activations.append(a)
        # Output layer
        z = a @ self.weights[-1] + self.biases[-1]
        self.zs.append(z)
        a = self.softmax(z)
        self.activations.append(a)
        return a

    def predict(self, x):
        return self.forward(x)

    def train(self, x, y_true):
        """
        Simple one-step training (cross-entropy loss)
        x: input vector (numpy)
        y_true: one-hot vector for target
        """
        output = self.forward(x)
        loss = -np.sum(y_true * np.log(output + 1e-8))

        # Backpropagation
        delta = output - y_true  # derivative of loss wrt softmax input
        for i in reversed(range(len(self.weights))):
            a_prev = self.activations[i]
            dw = np.outer(a_prev, delta)
            db = delta

            self.weights[i] -= self.lr * dw
            self.biases[i] -= self.lr * db

            if i > 0:
                dz = delta @ self.weights[i].T
                delta = dz * (self.zs[i-1] > 0)  # relu derivative

        return loss


class LFMTracker:
    """
    Learning-From-Mistakes Tracker.
    Tracks and learns from errors/exceptions in user code,
    provides detailed explanations and suggestions
    """

    def __init__(self,
                 max_history=100,
                 error_vector_size=50,
                 hidden_sizes=[64, 32],
                 suggestion_categories=5,
                 learning_rate=0.01,
                 verbose=True):
        """
        Parameters:
        - max_history: max number of tracked errors to store
        - error_vector_size: size of input vector 
        - hidden_sizes: list of hidden layers sizes 
        - suggestion_categories: number of suggestion types outputs
        - learning_rate: training rate
        - verbose: print tracking info
        """
        self.max_history = max_history
        self.error_vector_size = error_vector_size
        self.verbose = verbose
        self.history = []
        self.nn = SimpleNeuralNet(input_size=error_vector_size,
                                  hidden_sizes=hidden_sizes,
                                  output_size=suggestion_categories,
                                  lr=learning_rate)

    def _vectorize_error(self, error: Exception) -> np.ndarray:
        """
        Vectorizes the error into a fixed-size numerical vector.
        Uses traceback and error type information.
        """
        tb_str = ''.join(traceback.format_exception_only(type(error), error))
        tb_hash = hash(tb_str) % (10 ** 8)
        tb_vec = np.zeros(self.error_vector_size)

        # Simple vectorization: encode hash bits into vector
        for i in range(min(self.error_vector_size, 32)):
            tb_vec[i] = (tb_hash >> i) & 1

        # Add error type info (one hot for common types)
        error_types = ['ValueError', 'TypeError', 'IndexError', 'KeyError', 'ZeroDivisionError']
        for i, etype in enumerate(error_types):
            if etype == type(error).__name__:
                if i + 32 < self.error_vector_size:
                    tb_vec[i + 32] = 1

        return tb_vec

    def track_error(self, error: Exception, custom_msg: str = None):
        """
        Track an error occurrence and update model with feedback.
        """
        vec = self._vectorize_error(error)

        # Predict suggestions (softmax output)
        suggestions = self.nn.predict(vec)

        if self.verbose:
            print(f"[LFMTracker] Tracked error: {type(error).__name__}: {error}")
            print(f"[LFMTracker] suggestions (probabilities): {suggestions}")

        # Store history with timestamp and message
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append({'error': error, 'vector': vec, 'time': time.time(), 'msg': custom_msg})

        return suggestions

    def give_feedback(self, error: Exception, correct_category: int):
        """
        Train based on user feedback for the error category.
        correct_category: index of the correct suggestion category (0-based)
        """
        vec = self._vectorize_error(error)
        y_true = np.zeros(self.nn.biases[-1].shape)
        y_true[correct_category] = 1
        loss = self.nn.train(vec, y_true)
        if self.verbose:
            print(f"[LFMTracker] trained with feedback. Loss: {loss:.5f}")

    def report(self):
        """
        Prints a summary report of tracked errors.
        """
        print(f"\n[LFMTracker] Total errors tracked: {len(self.history)}")
        counts = {}
        for entry in self.history:
            etype = type(entry['error']).__name__
            counts[etype] = counts.get(etype, 0) + 1
        print("[LFMTracker] Error type counts:")
        for etype, count in counts.items():
            print(f"  {etype}: {count}")


class AutoRefactoringPrompter:
    """
    AutoRefactoringPrompter suggests refactorings for code smells and complexity,
    and can apply automated fixes (conceptual, not real code parsing).
    Uses a simple heuristic to rank suggestions.
    """

    def __init__(self,
                 max_function_length=50,
                 max_variable_name_length=20,
                 min_duplication_length=5,
                 max_duplicate_occurrences=3,
                 suggestion_categories=4,
                 hidden_sizes=[32, 16],
                 learning_rate=0.005,
                 verbose=True):
        """
        Parameters:
        - max_function_length: max allowed lines in a function before suggestion
        - max_variable_name_length: max allowed variable name length
        - min_duplication_length: min lines duplicated to suggest extraction
        - max_duplicate_occurrences: max duplicated occurrences to flag
        - suggestion_categories: number of refactor suggestions
        - hidden_sizes: hidden layers sizes for AI
        - learning_rate: training rate
        - verbose: print info
        """
        self.max_function_length = max_function_length
        self.max_variable_name_length = max_variable_name_length
        self.min_duplication_length = min_duplication_length
        self.max_duplicate_occurrences = max_duplicate_occurrences
        self.verbose = verbose
        self.nn = SimpleNeuralNet(input_size=5,
                                  hidden_sizes=hidden_sizes,
                                  output_size=suggestion_categories,
                                  lr=learning_rate)

    def analyze_code(self, code_str: str):
        """
        Analyzes code string to detect smells:
        - long functions
        - long variable names
        - duplicated lines (simple count)
        Returns a dict with analysis data.
        """
        lines = code_str.split('\n')
        functions = self._extract_functions(lines)
        long_funcs = [f for f in functions if len(f['lines']) > self.max_function_length]

        long_var_names = []
        for line in lines:
            words = line.strip().split()
            for w in words:
                if w.isidentifier() and len(w) > self.max_variable_name_length:
                    long_var_names.append(w)

        duplicates = self._detect_duplicates(lines)

        analysis = {
            'long_functions': len(long_funcs),
            'long_var_names': len(long_var_names),
            'duplicates': duplicates['count'],
            'duplicate_lines': duplicates['lines']
        }
        if self.verbose:
            print(f"[AutoRefactoring] Long funcs: {analysis['long_functions']}, Long vars: {analysis['long_var_names']}, Duplicates: {analysis['duplicates']}")
        return analysis

    def _extract_functions(self, lines):
        """
        Extracts function code blocks (very basic heuristic)
        Returns list of dict {name, lines}
        """
        functions = []
        current_func = None
        func_lines = []
        for line in lines:
            if line.strip().startswith("def "):
                if current_func is not None:
                    functions.append({'name': current_func, 'lines': func_lines})
                current_func = line.strip()
                func_lines = []
            elif current_func:
                func_lines.append(line)
        if current_func is not None:
            functions.append({'name': current_func, 'lines': func_lines})
        return functions

    def _detect_duplicates(self, lines):
        """
        Detects duplicated lines and their counts (naive).
        Returns dict with count and lines.
        """
        counts = {}
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                counts[line] = counts.get(line, 0) + 1
        duplicates = {line: cnt for line, cnt in counts.items() if cnt > 1}
        return {'count': len(duplicates), 'lines': duplicates}

    def suggest_refactors(self, code_str: str):
        """
        Uses to suggest best refactor action based on code analysis.
        Categories:
          0 - Extract Method
          1 - Rename Variables
          2 - Remove Duplicates
          3 - General Cleanup
        Returns category index and explanation.
        """
        analysis = self.analyze_code(code_str)
        feature_vector = np.array([
            analysis['long_functions'],
            analysis['long_var_names'],
            analysis['duplicates'],
            len(code_str),
            len(code_str.split('\n'))
        ], dtype=float)

        # Normalize features for AI input roughly
        feature_vector = feature_vector / (np.max(feature_vector) + 1e-5)

        prediction = self.nn.predict(feature_vector)
        suggestion_idx = int(np.argmax(prediction))

        suggestions_map = {
            0: "Extract long functions into smaller methods.",
            1: "Rename long or unclear variable names to concise ones.",
            2: "Remove duplicated code blocks by abstraction.",
            3: "Perform general code cleanup and formatting."
        }
        if self.verbose:
            print(f"[AutoRefactoring] suggestion: {suggestions_map[suggestion_idx]} (confidence {prediction[suggestion_idx]:.2f})")

        return suggestion_idx, suggestions_map[suggestion_idx]

    def train_feedback(self, feature_vector: np.ndarray, correct_suggestion: int):
        """
        Train  with feedback vector and correct category.
        """
        y_true = np.zeros(self.nn.biases[-1].shape)
        y_true[correct_suggestion] = 1
        loss = self.nn.train(feature_vector, y_true)
        if self.verbose:
            print(f"[AutoRefactoring] trained with feedback. Loss: {loss:.5f}")
