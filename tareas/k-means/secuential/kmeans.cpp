//#include <algorithm>
#include <cassert>
#include <chrono>
//#include <cstdlib>
#include <fstream>
#include <iostream>
//#include <limits>
#include <random>
#include <sstream>
#include <vector>
#include <math.h>

using namespace std;
/*
struct Point {
  double x{0}, y{0};
};*/

struct Point {
  vector<double>;
};

//vector<vector<double>>;

using DataFrame = vector<Point>;


double squared_l2_distance(vector& f, vector& s){
  double suma = 0;
  for(int i = 0; i<f.size();++i){
    suma += (f[i] - s[i])*(f[i] - s[i]);
  }
  return sqrt(suma);
}
/*
double squared_l2_distance(Point first, Point second) {

	return sqrt(((first.x - second.x)*(first.x - second.x)) + ((first.y - second.y)*(first.y - second.y)));
}*/

DataFrame k_means(const DataFrame& data, unsigned k, unsigned number_of_iterations, const DataFrame& cluster) {//, const DataFrame& centroides


  static random_device seed;
  static mt19937 random_number_generator(seed());
  uniform_int_distribution<unsigned> indices(0, data.size() - 1);


  // Pick centroids as random points from the dataset.
  DataFrame means(k);
  /* Genere cluster with aleatory points
  for (Point& cluster : means) {
    cluster = data[indices(random_number_generator)];
  }*/

  vector<unsigned int> assignments(data.size());
  for (unsigned int iteration = 0; iteration < number_of_iterations; ++iteration) {
    // Find assignments.
    for (unsigned int point = 0; point < data.size(); ++point) {
      double best_distance = numeric_limits<double>::max();
      unsigned int best_cluster = 0;
      for (unsigned int cluster = 0; cluster < k; ++cluster) {
        const double distance = squared_l2_distance(data[point], means[cluster]);
        if (distance < best_distance) {
          best_distance = distance;
          best_cluster = cluster;
        }
      }
      assignments[point] = best_cluster;
    }
 	//cout<<"they are the cluster: "<<cluster<<endl;

    // Sum up and count points for each cluster.
    DataFrame new_means(k);
    vector<unsigned int> counts(k, 0);
    for (unsigned int point = 0; point < data.size(); ++point) {
      const unsigned int cluster = assignments[point];
      //recorro el vector con las dimensiones


      new_means[cluster].x += data[point].x;
      new_means[cluster].y += data[point].y;
      counts[cluster] += 1;
    }

    // Divide sums by counts to get new centroids.
    for (unsigned int cluster = 0; cluster < k; ++cluster) {
      // Turn 0/0 into 0/1 to avoid zero division.
      const unsigned int count = max<size_t>(1, counts[cluster]);
      //recorro el vector


      means[cluster].x = new_means[cluster].x / count;
      means[cluster].y = new_means[cluster].y / count;
    }
  }

  return means;
}

int main(int argc, const char* argv[]) {
  if (argc < 4) {
    cerr << "excecute: kmeans.cpp <data-file> <k> [runs] <data-cluster>"
              << endl;
    exit(EXIT_FAILURE);
  }
  const auto dim = atoi(argv[2]);
  const auto k = atoi(argv[3]);
  //const auto iterations = (argc >= 4) ? atoi(argv[3]) : 300;
  unsigned int iterations = 1000;
  const unsigned int number_of_runs = (argc <= 15) ? atoi(argv[4]) : 15;
  /*
  DataFrame data;
  ifstream stream(argv[1]);
  if (!stream) {
    cerr << "Could not open file: " << argv[1] << endl;
    exit(EXIT_FAILURE);
  }
  string line;
  while (getline(stream, line)) {
    Point point;
    istringstream line_stream(line);
    size_t label;
    line_stream >> point.x >> point.y >> label;
    data.push_back(point);
  }*/

  DataFrame data;
  ifstream stream(argv[1]);
  if (!stream) {
    cerr << "Could not open file: " << argv[1] << endl;
    exit(EXIT_FAILURE);
  }
  string line;
  while (getline(stream, line)) {

    int n = 0;
    string token;
    string delimiter = ",";
    size_t pos = 0;
    while ((pos = line.find(delimiter)) != std::string::npos) {

      token = line.substr(0, pos);
      //cout << stod(token) << " ";
      data.push_back(stod(token));
      line.erase(0, pos + delimiter.length());
      n++;

      if(n >= dim)
        break;
    }
    /*
    Point point;
    istringstream line_stream(line2);
    size_t label;
    line_stream >> point.x >> point.y >> label;
    centroides.push_back(point);*/
  }
//leo argumentos los centroides iniciales
  
  DataFrame centroides;
  ifstream stream2(argv[5]);
  if (!stream2) {
    cerr << "Could not open file: " << argv[5] << endl;
    exit(EXIT_FAILURE);
  }
  string line2;
  while (getline(stream2, line2)) {

    int n = 0;
    string token;
    string delimiter = ",";
    size_t pos = 0;
    while ((pos = line2.find(delimiter)) != std::string::npos) {

      token = line2.substr(0, pos);
      //cout << stod(token) << " ";
      centroides.push_back(stod(token));
      line2.erase(0, pos + delimiter.length());
      n++;

      if(n >= dim)
        break;
    }
    /*
    Point point;
    istringstream line_stream(line2);
    size_t label;
    line_stream >> point.x >> point.y >> label;
    centroides.push_back(point);*/
  }

/*
  string linea;
  ifstream fileofpoints(nameFile);

  //travel line to line in the file
  if( fileofpoints.is_open()) {

    while( getline( fileofpoints, linea)){
      //cout << linea << endl;

      int n = 0;
      string token;
      string delimiter = ",";
      size_t pos = 0;
      while ((pos = linea.find(delimiter)) != std::string::npos) {

        token = linea.substr(0, pos);
        //cout << stod(token) << " ";
        points.push_back(stod(token));
        linea.erase(0, pos + delimiter.length());
        n++;

        if(n >= dim)
          break;

      }
      //cout << endl;
    }
*/

  DataFrame means;
  double total_elapsed = 0;
  for (int run = 0; run < number_of_runs; ++run) {
    const auto start = chrono::high_resolution_clock::now();
    means = k_means(data, k, iterations,centroides);
    const auto end = chrono::high_resolution_clock::now();
    const auto duration =
        chrono::duration_cast<chrono::duration<double>>(end - start);
    total_elapsed += duration.count();
  }
  cerr << "Took: " << total_elapsed / number_of_runs << "s ("
            << number_of_runs << " runs)" << endl;

  for (auto& mean : means) {
    cout << mean.x << " " << mean.y << endl;
  }
  cout<<"\n";
}