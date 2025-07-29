"""
Implementasi Algoritma Komodo Mlipir (KMA) dengan Clean Code dan PEP8.

Metode oleh:
    Prof. Dr. Suyanto, S.T., M.Sc. (2021)

Implementasi Python oleh:
    Pejalan Sunyi (2025)
"""

from typing import Callable, List, Tuple, Optional
import numpy as np
import math


class KomodoMlipirAlgorithm:
    """
    Implementasi Algoritma Komodo Mlipir untuk optimasi.
    
    Algoritma ini mensimulasikan perilaku komodo dalam mencari makanan
    dengan membagi populasi menjadi jantan besar, betina, dan jantan kecil.
    
    Attributes:
        population_size: Jumlah individu dalam populasi
        male_proportion: Proporsi jantan besar dalam populasi (0-1)
        mlipir_rate: Tingkat mlipir untuk pergerakan jantan kecil (0-1)
        fitness_function: Fungsi objektif yang akan dioptimalkan
        search_space: Batasan pencarian untuk setiap dimensi
        max_iterations: Jumlah iterasi maksimum
        random_state: Seed untuk reproduktibilitas
        parthenogenesis_radius: Radius untuk reproduksi aseksual
        stop_criteria: Kriteria konvergensi
        stop: Boolean untuk memeriksa konvergensi
    """
    
    def __init__(
        self,
        population_size: int = 5,
        male_proportion: float = 0.5,
        mlipir_rate: float = 0.5,
        fitness_function: Optional[Callable] = None,
        search_space: Optional[List[Tuple[float, float]]] = None,
        max_iterations: int = 1000,
        random_state: int = 42,
        parthenogenesis_radius: float = 0.1,
        stop_criteria: float = 0.01,
        stop: bool = False
    ):
        """Inisialisasi parameter algoritma KMA."""
        self._validate_parameters(
            population_size, male_proportion, mlipir_rate,
            fitness_function, search_space, max_iterations
        )
        
        self.population_size = population_size
        self.male_proportion = male_proportion
        self.mlipir_rate = mlipir_rate
        self.n_big_males = math.floor((1 - male_proportion) * population_size)
        self.fitness_function = fitness_function
        self.search_space = search_space
        self.max_iterations = max_iterations
        self.random_state = random_state
        self.parthenogenesis_radius = parthenogenesis_radius
        self.stop_criteria = stop_criteria
        self.stop = stop
        
        # Initialize random number generators
        np.random.seed(self.random_state)
        self.rng = np.random.default_rng(self.random_state)
        
        # Initialize population and fitness
        self.population = self._initialize_population()
        self.fitness_values = np.zeros(self.population_size)
        
        # Initialize tracking variables
        self.history = {"best_fitness": [], "best_solution": []}
        self.best_fitness = None
        self.best_solution = None
        
    def _validate_parameters(
        self,
        population_size: int,
        male_proportion: float,
        mlipir_rate: float,
        fitness_function: Callable,
        search_space: List[Tuple[float, float]],
        max_iterations: int
    ) -> None:
        """Validasi parameter input."""
        if population_size < 5:
            raise ValueError("Population size must be at least 3")
        
        if not 0.1 <= male_proportion <= 1:
            raise ValueError("Male proportion must be between 0.1 and 1")
        
        if not 0 <= mlipir_rate <= 1:
            raise ValueError("Mlipir rate must be between 0 and 1")
        
        if fitness_function is None:
            raise ValueError("Fitness function must be provided")
        
        if search_space is None or len(search_space) == 0:
            raise ValueError("Search space must be defined")
        
        if max_iterations < 1:
            raise ValueError("Maximum iterations must be at least 1")
    
    def _initialize_population(self) -> np.ndarray:
        """Inisialisasi populasi dengan distribusi uniform."""
        dimensions = len(self.search_space)
        population = self.rng.uniform(0, 1, (self.population_size, dimensions))
        
        # Scale to search space
        for i, (lower, upper) in enumerate(self.search_space):
            population[:, i] = lower + (upper - lower) * population[:, i]
        
        return population
    
    def _calculate_fitness(self, individuals: np.ndarray) -> np.ndarray:
        """
        Hitung nilai fitness untuk setiap individu.
        
        Args:
            individuals: Array individu yang akan dievaluasi
            
        Returns:
            Array nilai fitness
        """
        return np.array([
            self.fitness_function(individual) 
            for individual in individuals
        ])
    
    def _clip_to_bounds(self, individual: np.ndarray) -> np.ndarray:
        """
        Batasi nilai individu agar tetap dalam search space.
        
        Args:
            individual: Individu yang akan dibatasi
            
        Returns:
            Individu yang telah dibatasi
        """
        return np.array([
            np.clip(value, lower, upper)
            for value, (lower, upper) in zip(individual, self.search_space)
        ])
    
    def _sort_by_fitness(
        self, 
        population: np.ndarray, 
        fitness_values: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Urutkan populasi berdasarkan fitness (descending).
        
        Args:
            population: Array populasi
            fitness_values: Array nilai fitness
            
        Returns:
            Tuple populasi dan fitness yang telah diurutkan
        """
        sort_indices = np.argsort(fitness_values)[::-1]
        return population[sort_indices], fitness_values[sort_indices]
    
    def _divide_population(
        self, 
        sorted_population: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Bagi populasi menjadi jantan besar, betina, dan jantan kecil.
        
        Args:
            sorted_population: Populasi yang telah diurutkan
            
        Returns:
            Tuple (jantan_besar, betina, jantan_kecil)
        """
        big_males = sorted_population[:self.n_big_males]
        female = sorted_population[self.n_big_males]
        small_males = sorted_population[self.n_big_males + 1:]
        
        return big_males, female, small_males
    
    def _move_big_males(
        self, 
        big_males: np.ndarray, 
        fitness_values: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update posisi jantan besar berdasarkan interaksi antar individu.
        
        Args:
            big_males: Array jantan besar
            fitness_values: Nilai fitness jantan besar
            
        Returns:
            Tuple jantan besar dan fitness yang telah diupdate
        """
        n_males = len(big_males)
        movement_vectors = np.zeros_like(big_males)
        
        # Calculate movement for each big male
        for i in range(n_males):
            for j in range(n_males):
                if i != j:
                    movement_vectors[i] += self._calculate_male_interaction(
                        big_males[i], big_males[j],
                        fitness_values[i], fitness_values[j]
                    )
        
        # Update positions
        new_males = big_males + movement_vectors
        new_males = np.array([
            self._clip_to_bounds(male) for male in new_males
        ])
        
        # Evaluate new positions
        new_fitness = self._calculate_fitness(new_males)
        
        # Select best individuals
        return self._select_best_males(
            big_males, new_males, fitness_values, new_fitness
        )
    
    def _calculate_male_interaction(
        self,
        male_i: np.ndarray,
        male_j: np.ndarray,
        fitness_i: float,
        fitness_j: float
    ) -> np.ndarray:
        """Hitung vektor interaksi antara dua jantan."""
        r1 = self.rng.standard_normal()
        r2 = self.rng.standard_normal()
        
        if fitness_j < fitness_i and r2 < 0.5:
            return r1 * (male_j - male_i)
        else:
            return r1 * (male_i - male_j)
    
    def _select_best_males(
        self,
        old_males: np.ndarray,
        new_males: np.ndarray,
        old_fitness: np.ndarray,
        new_fitness: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Pilih jantan terbaik dari generasi lama dan baru."""
        all_males = np.vstack([old_males, new_males])
        all_fitness = np.concatenate([old_fitness, new_fitness])
        
        sorted_males, sorted_fitness = self._sort_by_fitness(
            all_males, all_fitness
        )
        
        return (
            sorted_males[:self.n_big_males], 
            sorted_fitness[:self.n_big_males]
        )
    
    def _move_female(
        self, 
        best_male: np.ndarray, 
        female: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update posisi betina melalui mating atau parthenogenesis.
        
        Args:
            best_male: Jantan terbaik
            female: Individu betina
            
        Returns:
            Tuple betina baru dan nilai fitnessnya
        """
        if self.rng.standard_normal() >= 0.5:
            return self._perform_mating(best_male, female)
        else:
            return self._perform_parthenogenesis(female)
    
    def _perform_mating(
        self, 
        male: np.ndarray, 
        female: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Lakukan perkawinan antara jantan dan betina."""
        r1 = self.rng.standard_normal()
        
        # Generate two offspring
        offspring1 = r1 * male + (1 - r1) * female
        offspring2 = r1 * female + (1 - r1) * male
        
        offspring1 = self._clip_to_bounds(offspring1)
        offspring2 = self._clip_to_bounds(offspring2)
        
        # Select best offspring
        fitness1 = self.fitness_function(offspring1)
        fitness2 = self.fitness_function(offspring2)
        
        if fitness2 >= fitness1:
            return np.array([offspring2]), np.array([fitness2])
        else:
            return np.array([offspring1]), np.array([fitness1])
    
    def _perform_parthenogenesis(
        self, 
        female: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Lakukan reproduksi aseksual (parthenogenesis)."""
        r = self.rng.standard_normal()
        
        # Calculate search space ranges
        ranges = np.array([
            abs(upper - lower) 
            for lower, upper in self.search_space
        ])
        
        # Generate offspring
        offspring = female + (2 * r - 1) * self.parthenogenesis_radius * ranges
        offspring = self._clip_to_bounds(offspring)
        
        fitness = self.fitness_function(offspring)
        
        return np.array([offspring]), np.array([fitness])
    
    def _move_small_males(
        self, 
        big_males: np.ndarray, 
        small_males: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update posisi jantan kecil berdasarkan mlipir behavior.
        
        Args:
            big_males: Array jantan besar
            small_males: Array jantan kecil
            
        Returns:
            Tuple jantan kecil dan fitness yang telah diupdate
        """
        new_small_males = np.copy(small_males)
        
        for i, small_male in enumerate(new_small_males):
            movement = self._calculate_mlipir_movement(
                small_male, big_males
            )
            new_small_males[i] = small_male + movement
        
        # Clip to bounds
        new_small_males = np.array([
            self._clip_to_bounds(male) for male in new_small_males
        ])
        
        fitness_values = self._calculate_fitness(new_small_males)
        
        return new_small_males, fitness_values
    
    def _calculate_mlipir_movement(
        self, 
        small_male: np.ndarray, 
        big_males: np.ndarray
    ) -> np.ndarray:
        """Hitung vektor pergerakan mlipir untuk jantan kecil."""
        movement = np.zeros_like(small_male)
        
        for big_male in big_males:
            for dim in range(len(small_male)):
                if self.rng.standard_normal() < self.mlipir_rate:
                    r1 = self.rng.standard_normal()
                    movement[dim] += r1 * (big_male[dim] - small_male[dim])
        
        return movement
    
    def _generate_new_individuals(
        self, 
        best_individual: np.ndarray, 
        n_individuals: int = 5
    ) -> np.ndarray:
        """Generate individu baru di sekitar individu terbaik."""
        new_individuals = []
        
        for _ in range(n_individuals):
            r = self.rng.standard_normal(size=len(best_individual))
            new_individual = best_individual + r
            new_individual = self._clip_to_bounds(new_individual)
            new_individuals.append(new_individual)
        
        return np.array(new_individuals)
    
    def _apply_adaptive_schema(
        self, 
        min_population: int = 20, 
        max_population: int = 200
    ) -> None:
        """
        Terapkan skema adaptif untuk menyesuaikan ukuran populasi.
        
        Args:
            min_population: Ukuran populasi minimum
            max_population: Ukuran populasi maksimum
        """
        if len(self.history["best_fitness"]) < 3:
            return
        
        # Calculate fitness improvements
        f1, f2, f3 = self.history["best_fitness"][-3:]
        df1 = abs(f1 - f2) / f1 if f1 != 0 else 0
        df2 = abs(f2 - f3) / f2 if f2 != 0 else 0
        
        # Sort population by fitness
        sorted_pop, sorted_fit = self._sort_by_fitness(
            self.population, self.fitness_values
        )
        
        current_size = len(self.population)
        
        # Shrink population if improving
        if df1 > 0 and df2 > 0 and current_size - 5 >= min_population:
            self.population = sorted_pop[:current_size - 5]
            self.fitness_values = sorted_fit[:current_size - 5]
            self.population_size = len(self.population)
        
        # Expand population if stagnant
        elif df1 == 0 and df2 == 0 and current_size + 5 <= max_population:
            new_individuals = self._generate_new_individuals(sorted_pop[0])
            new_fitness = self._calculate_fitness(new_individuals)
            
            self.population = np.vstack([self.population, new_individuals])
            self.fitness_values = np.concatenate([
                self.fitness_values, new_fitness
            ])
            self.population_size = len(self.population)
    
    def fit(
        self, 
        adaptive_schema: bool = False,
        min_population: int = 20,
        max_population: int = 100,
        verbose: bool = True
    ) -> None:
        """
        Jalankan proses optimasi.
        
        Args:
            adaptive_schema: Aktifkan skema adaptif
            min_population: Ukuran populasi minimum untuk skema adaptif
            max_population: Ukuran populasi maksimum untuk skema adaptif
            verbose: Tampilkan progress
        """
        # Initial fitness calculation
        self.fitness_values = self._calculate_fitness(self.population)
        
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"Iteration {iteration + 1}, "
                      f"Population size: {len(self.population)}")
            
            # Sort population
            self.population, self.fitness_values = self._sort_by_fitness(
                self.population, self.fitness_values
            )
            
            # Divide population
            big_males, female, small_males = self._divide_population(
                self.population
            )
            
            # Get fitness values for each group
            n_big = len(big_males)
            fitness_big = self.fitness_values[:n_big]
            fitness_female = self.fitness_values[n_big]
            fitness_small = self.fitness_values[n_big + 1:]
            
            # Move populations
            if verbose:
                print("  - Moving big males...")
            big_males, fitness_big = self._move_big_males(
                big_males, fitness_big
            )
            
            if verbose:
                print("  - Moving female...")
            female, fitness_female = self._move_female(big_males[0], female)
            
            if verbose:
                print("  - Moving small males...")
            small_males, fitness_small = self._move_small_males(
                big_males, small_males
            )
            
            # Combine populations
            self.population = np.vstack([big_males, small_males, female])
            self.fitness_values = np.concatenate([
                fitness_big, fitness_small, fitness_female
            ])
            
            # Update best solution
            self._update_best_solution()
            
            if verbose:
                print(f"  Best fitness: {self.best_fitness:.6f}")
            
            # Apply adaptive schema if enabled
            if adaptive_schema:
                self._apply_adaptive_schema(min_population, max_population)
            
            # Check stopping criteria
            if self._check_convergence() and self.stop:
                if verbose:
                    print(f"Converged at iteration {iteration + 1}")
                break
    
    def _update_best_solution(self) -> None:
        """Update solusi terbaik yang ditemukan."""
        current_best_idx = np.argmax(self.fitness_values)
        current_best_fitness = self.fitness_values[current_best_idx]
        
        if self.best_fitness is None or current_best_fitness > self.best_fitness:
            self.best_fitness = current_best_fitness
            self.best_solution = self.population[current_best_idx].copy()
        
        self.history["best_fitness"].append(self.best_fitness)
        self.history["best_solution"].append(self.best_solution.copy())
    
    def _check_convergence(self) -> bool:
        """Periksa apakah algoritma telah konvergen."""
        if len(self.history["best_fitness"]) < 10:
            return False
        
        recent_fitness = self.history["best_fitness"][-10:]
        fitness_std = np.std(recent_fitness)
        
        return fitness_std < self.stop_criteria
    
    def get_results(self) -> dict:
        """
        Dapatkan hasil optimasi.
        
        Returns:
            Dictionary berisi solusi terbaik dan riwayat optimasi
        """
        return {
            "best_solution": self.best_solution,
            "best_fitness": self.best_fitness,
            "history": self.history,
            "n_iterations": len(self.history["best_fitness"])
        }


# Alias
KMA = KomodoMlipirAlgorithm