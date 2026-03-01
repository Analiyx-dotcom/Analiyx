import React from 'react';
import { testimonials } from '../mock/mockData';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Quote } from 'lucide-react';

const Testimonials = () => {
  return (
    <section className="py-20 bg-gradient-to-b from-gray-950 to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <p className="text-purple-400 text-sm font-semibold uppercase tracking-wider mb-2">Reviews</p>
          <h2 className="text-4xl font-bold text-white mb-4">Loved by data teams</h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            See why companies trust Papermap AI to turn messy data into actionable insights—without the wait.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {testimonials.map((testimonial) => (
            <Card
              key={testimonial.id}
              className="bg-gray-900/50 border-gray-800 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl hover:shadow-purple-500/10"
            >
              <CardContent className="p-8">
                <Quote className="w-10 h-10 text-purple-500/30 mb-4" />
                <blockquote className="text-xl font-semibold text-white mb-4">
                  "{testimonial.quote}"
                </blockquote>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  {testimonial.description}
                </p>
                <div className="flex items-center space-x-4">
                  <Avatar className="w-12 h-12 border-2 border-purple-500">
                    <AvatarFallback className="bg-gradient-to-br from-purple-600 to-pink-600 text-white font-semibold">
                      {testimonial.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-white font-semibold">{testimonial.name}</p>
                    <p className="text-gray-500 text-sm">{testimonial.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;