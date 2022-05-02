export function TSP(matrix){
    return quicklyTSP(matrix);
}

function quicklyTSP(matrix, initial = 0){
    let n = matrix.length;
    let visited = Array(n).fill(false);
    visited[initial] = true;
    let path = [initial];
    for(let i = 0; i < n - 1; i++){
        let min = Infinity;
        let next = -1;
        for(let j = 0; j < n; j++){
            if(!visited[j] && matrix[path[path.length - 1]][j] < min){
                min = matrix[path[path.length - 1]][j];
                next = j;
            }
        }
        visited[next] = true;
        path.push(next);
    }
    return path;
}