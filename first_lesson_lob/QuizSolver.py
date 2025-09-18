# 🎯 QUIZ SOLVER CLASS
# Clase para manejar quizzes educativos del LOB

# 📚 Importaciones necesarias
from IPython.display import HTML, display
import time

class QuizSolver:
    """
    � Clase para gestionar y mostrar quizzes educativos sobre Limit Order Books
    
    Esta clase maneja las respuestas, explicaciones y puntuaciones de los quizzes
    del notebook de LOB dinámico.
    """
    
    def __init__(self):
        self.quiz_title = "🎉 ¡RESPUESTAS DEL QUIZ LOB!"
        self.separator = "=" * 50
        
        # Respuestas predefinidas con explicaciones
        self.answers = {
            1: {
                'correct': 'C',
                'explanation': 'Las órdenes LIMIT especifican un precio exacto y esperan en el book hasta encontrar un match. Las órdenes MARKET se ejecutan inmediatamente al mejor precio disponible en ese momento.',
                'color': 'linear-gradient(135deg, #00b894, #00a085)'
            },
            2: {
                'correct': 'B',
                'explanation': 'Spread = Best Ask - Best Bid = $150.05 - $149.95 = $0.10. El spread representa el "costo de liquidez" del mercado.',
                'color': 'linear-gradient(135deg, #fdcb6e, #e17055)'
            },
            3: {
                'correct': 'B',
                'explanation': 'La Orden B se ejecuta primero porque tiene el mejor precio ($101.00). Las reglas de prioridad son: 1° PRECIO, 2° TIEMPO. Entre órdenes del mismo precio, aplica FIFO.',
                'color': 'linear-gradient(135deg, #a29bfe, #6c5ce7)'
            },
            4: {
                'correct': 'B',
                'explanation': 'El lado verde (BID) representa órdenes de compra ordenadas de mayor a menor precio. El precio más alto (Best Bid) está en la parte superior.',
                'color': 'linear-gradient(135deg, #00cec9, #00b894)'
            },
            5: {
                'correct': 'B',
                'explanation': 'Mid Price = (Best Bid + Best Ask) / 2. En nuestro ejemplo: ($149.95 + $150.05) / 2 = $150.00. Representa el precio "justo" teórico.',
                'color': 'linear-gradient(135deg, #74b9ff, #0984e3)'
            }
        }
    
    def show_quiz_answers(self):
        """
        � Muestra las respuestas correctas del quiz con explicaciones
        """
        
        print(self.quiz_title)
        print(self.separator)
        
        # Mostrar cada respuesta con un pequeño delay para mejor UX
        for question_num, answer_data in self.answers.items():
            answer_html = self._generate_answer_html(question_num, answer_data)
            display(HTML(answer_html))
            time.sleep(0.5)
        
        # Mostrar sección de puntuación
        score_html = self._generate_score_section()
        display(HTML(score_html))
        
        print("\n🎯 ¡Excelente trabajo completando el quiz!")
        print("🚀 ¡Ahora estás listo para el siguiente nivel: Simulación Interactiva!")
    
    def _generate_answer_html(self, question_num, answer_data):
        """
        🎨 Genera el HTML para mostrar una respuesta individual
        """
        question_titles = {
            1: "📝 Pregunta 1",
            2: "📊 Pregunta 2", 
            3: "⚡ Pregunta 3",
            4: "🎨 Pregunta 4",
            5: "🧮 Pregunta 5"
        }
        
        return f"""
        <div style='background: {answer_data['color']}; padding: 15px; border-radius: 8px; color: white; margin: 10px 0;'>
            <h4>{question_titles[question_num]}: Respuesta Correcta = <b>{answer_data['correct']}</b></h4>
            <p><b>✅ Explicación:</b> {answer_data['explanation']}</p>
        </div>
        """
    
    def _generate_score_section(self):
        """
        🏆 Genera la sección de evaluación final
        """
        return """
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 10px; color: white; text-align: center; margin: 20px 0;'>
            <h3>🏆 ¡EVALUACIÓN COMPLETADA!</h3>
            <p><b>¿Cuántas respuestas acertaste?</b></p>
            <ul style='text-align: left; margin: 20px auto; max-width: 300px;'>
                <li><b>5/5:</b> 🎉 ¡Experto en LOB!</li>
                <li><b>4/5:</b> 👍 ¡Muy bien!</li>
                <li><b>3/5:</b> 😊 Buen entendimiento</li>
                <li><b>2/5:</b> 🤔 Repasa los conceptos</li>
                <li><b>0-1/5:</b> 📚 Vuelve a leer la teoría</li>
            </ul>
        </div>
        """
    
    def show_single_answer(self, question_number):
        """
        🎯 Muestra la respuesta de una pregunta específica
        
        Args:
            question_number: Número de la pregunta (1-5)
        """
        if question_number in self.answers:
            answer_data = self.answers[question_number]
            answer_html = self._generate_answer_html(question_number, answer_data)
            display(HTML(answer_html))
        else:
            print(f"❌ Pregunta {question_number} no encontrada. Preguntas disponibles: 1-5")
    
    def get_quiz_stats(self):
        """
        📊 Retorna estadísticas del quiz
        """
        return {
            'total_questions': len(self.answers),
            'questions_available': list(self.answers.keys()),
            'quiz_title': self.quiz_title
        }